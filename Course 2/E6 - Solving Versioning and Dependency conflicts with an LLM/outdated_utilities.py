# Outdated Python 3 Script
import datetime
import imp  # Outdated module!

# 1. Outdated Module Import
# The 'imp' module was used for dynamic module loading, but it was 
# deprecated in Python 3.4 and completely REMOVED in Python 3.12.
# Running this on a modern machine will crash with a ModuleNotFoundError.


# 2. Outdated Datetime Method
# 'utcnow()' is deprecated in Python 3.12 because it doesn't specify a timezone,
# which can cause silent time-zone conversion bugs.
current_time_utc = datetime.datetime.utcnow()


# 3. Old-Style String Formatting
# While the '%' operator still works, it is considered outdated and less secure/readable
# than modern Python 3 string formatting.
greeting_message = "Hello %s, the current UTC time is %s" % ("Bruno", current_time_utc)

print(greeting_message)


# 4. Unsafe Resource Management
# Opening a file without a context manager leaves the file handle open if an error occurs,
# which can cause file locks and memory leaks.
file_handle = open("log.txt", "w")
file_handle.write("Log processed successfully.")
file_handle.close()