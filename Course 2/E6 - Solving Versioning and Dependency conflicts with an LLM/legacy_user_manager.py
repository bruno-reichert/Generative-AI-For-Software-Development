# Legacy Python 2 Script

# Mock database of users and their monthly subscription costs
user_costs = {
    "alice": 15,
    "bob": 30,
    "charlie": 25
}

# 1. Python 2 print statement
print "--- User Subscription Cost Manager ---"

# 2. Python 2 dictionary iteration
for name, cost in user_costs.iteritems():
    # 3. Python 2 division logic (integer division)
    # We want to find the daily cost assuming a 30-day month
    daily_cost = cost / 30
    
    print "User:", name, "| Daily cost:", daily_cost

print "\n--- Running Looped Processing ---"

# 4. Python 2 xrange loop
for i in xrange(3):
    print "Processing pass", i

# 5. Python 2 raw_input
new_user = raw_input("\nEnter a new username to register: ")
print "Registered user:", new_user