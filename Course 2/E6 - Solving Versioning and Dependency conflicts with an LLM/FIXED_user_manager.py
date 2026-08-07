import datetime

# 1. Removed 'imp' - dynamic loading is handled by importlib if needed.

# 2. Secure, timezone-aware UTC datetime retrieval (Python 3.12+ standard)
current_time_utc = datetime.datetime.now(datetime.timezone.utc)

# 3. Modern, clean f-string formatting
greeting_message = f"Hello {'Bruno'}, the current UTC time is {current_time_utc}"
print(greeting_message)

# 4. Safe Resource Management - 'with' automatically handles closing the file safely!
with open("log.txt", "w") as file_handle:
    file_handle.write("Log processed successfully.")