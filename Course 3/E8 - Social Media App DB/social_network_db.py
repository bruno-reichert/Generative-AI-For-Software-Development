from sqlalchemy import create_engine, ForeignKey, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, aliased

# =====================================================================
# 1. Initialize Database Engine (Local SQLite)
# =====================================================================
engine = create_engine("sqlite:///social_network.db", echo=False)


# =====================================================================
# 2. Database Schemas (Many-to-Many & Self-Referential)
# =====================================================================
class Base(DeclarativeBase):
    pass


class Person(Base):
    """Represents an individual in the social network."""
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class Club(Base):
    """Represents a club that people can join."""
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class Membership(Base):
    """Association table linking People to Clubs (Many-to-Many)."""
    __tablename__ = "memberships"

    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), primary_key=True)


class Friendship(Base):
    """
    Association table linking People to other People (Directed Many-to-Many).
    - person_id: The person who considers the other a friend (initiator).
    - friend_id: The person who is being considered a friend (recipient).
    """
    __tablename__ = "friendships"

    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    friend_id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)


# =====================================================================
# 3. Task Solvers (The 3 Required Assignment Queries)
# =====================================================================

def find_club_members(session: Session, club_name: str) -> list[str]:
    """
    Task 1: Finds all members of a given club.
    """
    query = (
        select(Person.name)
        .join(Membership, Person.id == Membership.person_id)
        .join(Club, Club.id == Membership.club_id)
        .where(Club.name == club_name)
    )
    return list(session.scalars(query).all())


def find_my_friends(session: Session, person_name: str) -> list[str]:
    """
    Task 2: Finds everyone that a specific person considers to be their friend.
    (Outgoing friendships: person_id -> friend_id)
    """
    # Create aliases because we are joining the 'people' table twice
    p = aliased(Person, name="person")
    f = aliased(Person, name="friend")

    query = (
        select(f.name)
        .join(Friendship, f.id == Friendship.friend_id)
        .join(p, p.id == Friendship.person_id)
        .where(p.name == person_name)
    )
    return list(session.scalars(query).all())


def find_who_considers_me_friend(session: Session, person_name: str) -> list[str]:
    """
    Task 3: Finds everyone who considers a specific person to be their friend.
    (Incoming friendships: friend_id <- person_id)
    """
    p = aliased(Person, name="person")
    f = aliased(Person, name="friend")

    query = (
        select(p.name)
        .join(Friendship, p.id == Friendship.person_id)
        .join(f, f.id == Friendship.friend_id)
        .where(f.name == person_name)
    )
    return list(session.scalars(query).all())


# =====================================================================
# 4. Database Seeder
# =====================================================================
def seed_social_network():
    """Wipes and seeds the social network database with a test network."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Create People
        alice = Person(name="Alice")
        bob = Person(name="Bob")
        charlie = Person(name="Charlie")
        david = Person(name="David")
        
        session.add_all([alice, bob, charlie, david])
        session.flush()

        # Create Clubs
        coding_club = Club(name="Python Coders")
        chess_club = Club(name="Chess Masters")
        
        session.add_all([coding_club, chess_club])
        session.flush()

        # Create Memberships
        session.add_all([
            # Python Coders has Alice, Bob, and Charlie
            Membership(person_id=alice.id, club_id=coding_club.id),
            Membership(person_id=bob.id, club_id=coding_club.id),
            Membership(person_id=charlie.id, club_id=coding_club.id),
            # Chess Masters has Charlie and David
            Membership(person_id=charlie.id, club_id=chess_club.id),
            Membership(person_id=david.id, club_id=chess_club.id)
        ])

        # Create Directed Friendships
        session.add_all([
            # Alice considers Bob and Charlie her friends (Outgoing from Alice)
            Friendship(person_id=alice.id, friend_id=bob.id),
            Friendship(person_id=alice.id, friend_id=charlie.id),
            
            # Bob considers Charlie his friend
            Friendship(person_id=bob.id, friend_id=charlie.id),
            
            # Charlie considers Alice his friend
            Friendship(person_id=charlie.id, friend_id=alice.id),
            
            # David considers Alice his friend (Alice has Bob, Charlie, and David as incoming friends!)
            Friendship(person_id=david.id, friend_id=alice.id)
        ])
        
        session.commit()


# =====================================================================
# 5. Executing the Graded Lab
# =====================================================================
if __name__ == "__main__":
    seed_social_network()

    with Session(engine) as session:
        print("==================================================")
        print("         SOCIAL NETWORK GRADED LAB TESTS          ")
        print("==================================================")

        # Task 1 Test: Find members of 'Python Coders'
        club_to_query = "Python Coders"
        members = find_club_members(session, club_to_query)
        print(f"\n[Task 1] Members of '{club_to_query}':")
        print(f"  -> {', '.join(members)} (Expected: Alice, Bob, Charlie)")

        # Task 2 Test: Find who Alice considers her friends
        person_query_1 = "Alice"
        my_friends = find_my_friends(session, person_query_1)
        print(f"\n[Task 2] People that '{person_query_1}' considers to be friends:")
        print(f"  -> {', '.join(my_friends)} (Expected: Bob, Charlie)")

        # Task 3 Test: Find who considers Alice their friend
        person_query_2 = "Alice"
        who_likes_me = find_who_considers_me_friend(session, person_query_2)
        print(f"\n[Task 3] People who consider '{person_query_2}' to be their friend:")
        print(f"  -> {', '.join(who_likes_me)} (Expected: Charlie, David)")
        
        print("\n==================================================")