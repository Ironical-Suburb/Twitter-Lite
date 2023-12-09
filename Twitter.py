import sqlite3
import argparse
import getpass
import random
import re
import os
from tkinter import Menu




def connect_to_database(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    
#connect to data base
parser = argparse.ArgumentParser(description="Connect to a SQLite database.")
parser.add_argument("db_file", help="SQLite database file name")
args = parser.parse_args()

db_connection = connect_to_database(args.db_file)
cursor = db_connection.cursor()

def main():
    
    if db_connection:
        print(f"Connected to the database: {args.db_file}")
        # You can perform database operations here  
        login_screen()
        db_connection.close()
        print("Database connection closed.")

def login_screen():
    global db_connection, cursor

    is_user = False
    clear_screen()

    # Tell the user they can press exit
    print("Enter e to exit the program at any time.")

    # ask the person if they are a new user or an existing user
    account_status = ""
    while(account_status != "l" or account_status != "c" ):
        print("Would you like to login or create a user account? (enter l for login and r to register)")
        account_status = input().strip().lower()

        if (account_status == "e"):
            exit()
        
        if (account_status == "l"):
            # get the User ID
            while not is_user:
            # Validate that the input is a positive integer
                while True:
                    try:
                        print("Enter L to go back to login page")
                        inputValue = input("Enter your userID: ").strip()
                        if inputValue == 'l' or inputValue == "L":
                            login_screen()
                        userID = int(inputValue)
                        if userID > 0:
                            break
                        else:
                            print("User ID must be a positive integer.")
                    except ValueError:
                        print("User ID must be a positive integer.")

                # check if the person is a user
                cursor.execute('''
                    SELECT *
                    FROM users
                    WHERE usr= ?
                    ;
                ''' , (userID,)
                )

                if (cursor.fetchone() != None):
                    is_user = True
                else:
                    print("Invalid user ID")
            

            # get password
            print("Press Enter to go back to login screen")
            
            password = getpass.getpass()

            if password == '':
                login_screen()

            cursor.execute('''
                SELECT *
                FROM users
                WHERE usr = ? AND pwd = ?
                ;
            ''' , (userID, password)
            )

            while(cursor.fetchone() == None):
                print("Incorrect password.")
                password = getpass.getpass()

                cursor.execute('''
                SELECT *
                FROM users
                WHERE usr = ? AND pwd = ?
                ;
            ''' , (userID, password)
            )
            clear_screen()
            userMenu(userID)
                
                
        elif (account_status == "r"):
            unique_id = False

            

            while (not unique_id):
                #look up user ID, generate userid until unique is found

                #generate unique username
                newUser = random.randint(10000, 99999)

                cursor.execute('''
                    SELECT usr
                    FROM users
                    WHERE usr = ?
    
                ''' , (newUser,)
                )

                if (cursor.fetchone() == None):
                    # the id is unique
                    unique_id = True

                print ("Type L to go back to login screen")
                print("Enter your name:")
                name = input().strip()
                if name == 'l' or name== 'L':
                    login_screen()
                while not (re.match(r'^[a-zA-Z ]+$', name) is not None):
                    print("Invalid name. Please enter a valid name:")
                    name = input().strip()

                #get and validate password
                correct = False
                while not correct:
                    print("Press Enter to go back to login screen")
                    password = getpass.getpass("Enter a password: ")
                    if password == '':
                        login_screen()
                    confirm_password = getpass.getpass("Confirm password: ")
                    if password == confirm_password:
                        correct = True
                    else:
                        print("Passwords does not match!")

               

                print("Enter your email:")
                print ("Type L to go back to login screen")
                uEmail = input().strip()
                if uEmail == 'l' or uEmail =="L":
                    login_screen()
                while not validate_email(uEmail):
                    print("Invalid email format. Please enter a valid email:")
                    uEmail = input().strip()

                print ("Type L to go back to login screen")
                print("Enter your city:")
                uCity = input().strip()
                if uCity == 'l' or uCity =="L":
                    login_screen()
                while not all(char.isalpha() or char.isspace() or char == '-' for char in uCity):
                    print("Invalid city name. Please enter a valid city name:")
                    uCity = input().strip()

                print ("Type L to go back to login screen")
                print("Enter your timezone:")
                uTimezone = input().strip()
                if uTimezone == 'l' or uTimezone =="L":
                    login_screen()
                while not validate_timezone(uTimezone):
                    print("Invalid timezone format. Please enter a valid timezone.")
                    uTimezone = input().strip()

                

                cursor.execute('''
                    INSERT INTO users VALUES (?, ?, ?, ?, ?,?);
                    ''',
                    (newUser, password, name, uEmail, uCity, uTimezone)
                )

                clear_screen()
                print("Your user ID is",newUser)
                userMenu(newUser)
                 
                
        elif (account_status == "e"):
            exit()


#Creating the system menu
def userMenu(user):

    
    


    # Get the list of users being followed by the provided user
    cursor.execute("SELECT flwee FROM follows WHERE flwer = ?", (user,))
    followed_users = [row[0] for row in cursor.fetchall()]

    if not followed_users:
        #print current user name
        cursor.execute('''
        SELECT name
        FROM users
        WHERE usr = ? ''' 
                    , (user,))
        name = cursor.fetchone()
        print("\nWelcome",name[0])

        print("You are not following any users.")
    else:

        # Create a list of placeholders for the IN clause
        placeholders = ",".join(["?"] * len(followed_users))
        # Retrieve tweets and retweets from followed users, ordered by date
        cursor.execute(
            "SELECT t.tid, u.name, t.tdate, t.text FROM tweets AS t "
            "INNER JOIN users AS u ON t.writer = u.usr "
            "WHERE t.writer IN ({}) "
            "UNION ALL "
            "SELECT r.tid, u.name, r.rdate, t.text FROM retweets AS r "
            "INNER JOIN users AS u ON r.usr = u.usr "
            "INNER JOIN tweets AS t ON r.tid = t.tid "
            "WHERE r.usr IN ({}) ".format(placeholders, placeholders),
            followed_users + followed_users,  # Duplicate the list for parameter binding
        )

        tweets = cursor.fetchall()

        # Sort the tweets by date in descending order
        tweets.sort(key=lambda x: x[2], reverse=True)

        # Display tweets in batches of 5
        batch_size = 5
        start = 0
        running = True
        while running:

            if start < len(tweets):
                #print current user name
                cursor.execute('''
                SELECT name
                FROM users
                WHERE usr = ? ''' 
                            , (user,))
                name = cursor.fetchone()
                print("\nWelcome",name[0])

                end = min(start + batch_size,len(tweets))
                current_batch = tweets[start:end]

                print("Tweets:")
                for tweet in current_batch:
                    tid, name, tdate, text = tweet
                    tweet_line = f"User: {name}, Date: {tdate}, Tweet: {text}, Tweet ID: {tid}"
                    print(tweet_line)


                start = end


                
            print("\nTo exit the program at any time, type e.\n")

            #Main Menu
            print("Select from the following options: ")
            print("Type 1 to Search for tweets ")

            print("Type 2 to Search for users")

            print("Type 3 to Compose a tweet.")

            print("Type 4 to List followers.")

            print("Type N to go to next page.")


            print("Type L to logout, or Q to quit\n")

            option = input("Select your action using the options above: ")
            validInput = True
            while validInput == True: 
                if (option.isnumeric() == True):
                    if int(option) == 1:
                        clear_screen()
                        search_for_tweets(user)

                    elif int(option) == 2:
                        clear_screen()
                        list_users(user)

                    elif int(option) == 3:
                        clear_screen()
                        reply_to = None
                        compose_tweet(user, reply_to)

                    elif int(option) == 4:
                        list_followers(user)

                    else:
                        clear_screen()
                        print("Invalid entry")
                        validInput = False


                elif option.upper() == 'Q':
                    #end session 

                    quit()

                elif option.upper() == 'L':
                    #go to login screen
                    login_screen()

                elif option.upper() == 'N':
                    # Ask the user if they want to see more tweets
                    if start < len(tweets):
                        clear_screen()
                        validInput = False
                    else:
                        print("No more tweets")
                        validInput = False

                else:
                    clear_screen()
                    print("Invalid entry")
                    validInput = False




def search_for_tweets(usr_id):
    # Ask for user input
    print("Press Enter to go back to Menu")
    print('Please enter one or more keywords of the tweet you wanna search:')
    user_input = input()
    if user_input == "":
        clear_screen()
        userMenu(usr_id)
    keywords = user_input.split()

    hashtags = [word[1:] for word in keywords if word.startswith('#')]
    plain_keywords = [word for word in keywords if not word.startswith('#')]
    # Construct the WHERE clause
    hashtag_conditions = ' OR '.join(['mentions.term LIKE ?' for _ in hashtags])
    text_conditions = ' OR '.join(['tweets.text LIKE ?' for _ in plain_keywords])
    where_conditions = ' OR '.join(filter(None, [hashtag_conditions, text_conditions])) 
    # If there are no conditions, return an empty list
    if not where_conditions:
        return []

    query = f'''
        SELECT DISTINCT tweets.tid, tweets.writer, tweets.tdate, tweets.text
        FROM tweets
        LEFT JOIN mentions ON tweets.tid = mentions.tid
        WHERE {where_conditions}
        ORDER BY tweets.tdate DESC;
    '''
    params = tuple([hashtag.strip('#') for hashtag in hashtags] + [f'%{keyword}%' for keyword in plain_keywords])
    cursor.execute(query, params)

    tweets = cursor.fetchmany(5)
    
    if not tweets:
        print('No results found')
        print("Enter E to exit")
        print("Enter anything to search a different keyword")
        enteredValue = input().strip().lower()
        if enteredValue == 'e':
            clear_screen()
            userMenu(usr_id)
        else:
            return
  
    user_option = 'n'
    while True:
        if tweets and user_option == 'n':
            print('The search results are:\n')

            for tweet in tweets:
                print(f"Tweet ID: {tweet[0]}, Writer ID: {tweet[1]}, Date: {tweet[2]}, Text: {tweet[3]}")


        print('Type N to see more tweets')
        print('Type S to see stats for tweets')
        print('Type E to exit')


        user_option = input().strip().lower()

        if user_option == 'n':
            tweets = cursor.fetchmany(5)
            if not tweets:
                print('No more tweets found')

        if user_option == 's':
            get_tweet_stats(usr_id)


        elif user_option =='e':
            clear_screen()
            userMenu(usr_id)

        if user_option!='n' and user_option!='s' and user_option!='e':
            print('Please enter n, s or e')
        
        

    


# Email validation function
def validate_email(email):
    # Regular expression to validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

# Timezone validation function
def validate_timezone(timezone):
    try:
        float_timezone = float(timezone)
        # If it successfully converts to a float, it's valid
        return True
    except ValueError:
        # If a ValueError is raised, it's not a valid float
        return False

# Search and list User function 
def list_users(current_user):
    print("Press Enter to go back to Menu")
    print("Enter a keyword to search for users:")
    keyword = input().strip().lower()
    if keyword== "":
        clear_screen()
        login_screen()

    # Query for users whose names match the keyword
    name_match_query = '''
    SELECT usr, name, city
    FROM users
    WHERE LOWER(name) LIKE ?
    ORDER BY LENGTH(name)
    '''

    # Query for users whose cities match the keyword but names do not
    city_match_query = '''
    SELECT usr, name, city
    FROM users
    WHERE LOWER(city) LIKE ? AND LOWER(name) NOT LIKE ?
    ORDER BY LENGTH(city)
    '''

    params_name = (f'%{keyword}%',)
    params_city = (f'%{keyword}%', f'%{keyword}%')

    cursor.execute(name_match_query, params_name)
    name_matches = cursor.fetchall()

    cursor.execute(city_match_query, params_city)
    city_matches = cursor.fetchall()

    # Combine the results
    users = name_matches + city_matches


    # Display the results with pagination
    start = 0
    end = start + 5
    while True:
        for user in users[start:end]:
            print(f"User ID: {user[0]}, Name: {user[1]}, City: {user[2]}")

        if end < len(users):
            print("Enter 'more' to see more users, 'q' to return, or a user ID for more details:")
        else:
            print("No user found try again ... Enter 'q' to return or a user ID for more details:")

        choice = input().strip().lower()

        if choice.isdigit():
            selected_user = int(choice)
            if any(user[0] == selected_user for user in users):
                show_user_details_and_tweets(selected_user, current_user)
            else:
                print("Invalid user ID.")
        elif choice == 'more' and end < len(users):
            start = end
            end = min(end + 5, len(users))
        elif choice == 'q':
            clear_screen()    
            userMenu(current_user)
        else:
            print("Invalid input.")

def show_user_details_and_tweets(selected_user, current_user):
    # Fetching user details
    cursor.execute("SELECT name, city, email FROM users WHERE usr = ?", (selected_user,))
    user_details = cursor.fetchone()
    print(f"Name: {user_details[0]}, City: {user_details[1]}, Email: {user_details[2]}")

    # Fetching tweet count
    cursor.execute("SELECT COUNT(*) FROM tweets WHERE writer = ?", (selected_user,))
    tweet_count = cursor.fetchone()[0]
    print(f"Number of Tweets: {tweet_count}")

    # Fetching followers and following count
    followers_count, following_count = get_following_and_followers(selected_user)
    print(f"Number of Followers: {followers_count}, Number of Following: {following_count}")

    # Pagination setup for tweets
    batch_size = 5
    start_index = 0

    # Loop for displaying tweets and options
    while True:
        # Fetching a batch of tweets
        cursor.execute("SELECT tid, tdate, text FROM tweets WHERE writer = ? ORDER BY tdate DESC LIMIT ? OFFSET ?", (selected_user, batch_size, start_index))
        tweets = cursor.fetchall()

        # Display the tweets
        if tweets:
            print("\nMost Recent Tweets:")
            for tweet in tweets:
                print(f"Tweet ID: {tweet[0]}, Date: {tweet[1]}, Text: {tweet[2]}")

        # Options
        print("\nOptions: [F] Follow User, [M] More Tweets, [B] Back")
        choice = input("Enter your choice: ").upper()

        if choice == "F":
            follow_user(current_user, selected_user)
        elif choice == "M":
            if len(tweets) < batch_size:
                print("No more tweets available.")
            else:
                start_index += batch_size  # Increment to get the next batch of tweets
        elif choice == "B":
            break
        else:
            print("Invalid option selected.")

        if len(tweets) < batch_size:
            print("No more tweets to display.")
            break


def follow_user(current_user, selected_user):
    # Functionality to follow a user
    cursor.execute("SELECT * FROM follows WHERE flwer = ? AND flwee = ?", (current_user, selected_user))
    if cursor.fetchone():
        print("You are already following this user.")
    else:
        # Follow the selected user
        cursor.execute("INSERT INTO follows (flwer, flwee, start_date) VALUES (?, ?, CURRENT_DATE)", (current_user, selected_user))
        db_connection.commit()
        print("You are now following this user.")
    

def compose_tweet(user_id, reply_to):
    print("Press Enter to go back to Menu")
    tweet_text = input("Compose your tweet: ")
    if tweet_text== '':
        clear_screen()
        userMenu(user_id)
    # Extract hashtags from the tweet text
    hashtags = [word[1:] for word in tweet_text.split() if word.startswith("#")]
    # Get the ID of the newly inserted tweet
    tweet_id = get_tid() 
    # Insert the tweet into the tweets table
    cursor.execute("INSERT INTO tweets (tid, writer, tdate, text, replyto) VALUES (?, ?, CURRENT_DATE, ?, ?)", (tweet_id, user_id, tweet_text, reply_to))
    db_connection.commit()
    
    for hashtag in hashtags:
        # Insert the hashtag into the mentions table
        cursor.execute("INSERT INTO mentions (tid, term) VALUES (?, ?)", (tweet_id, hashtag))
        
        # Check if the hashtag exists in the hashtags table, and insert it if not
        cursor.execute("SELECT term FROM hashtags WHERE term = ?", (hashtag,))
        existing_hashtag = cursor.fetchone()
        
        if not existing_hashtag:
            cursor.execute("INSERT INTO hashtags (term) VALUES (?)", (hashtag,))
    
    db_connection.commit()
    
    print("Tweet posted successfully!")

def get_tid():
    cursor.execute("SELECT MAX(tid) FROM tweets")
    max_tid = cursor.fetchone()[0]
    
    if max_tid is not None:
        return max_tid + 1
    else:
        return 1


def list_followers(user_id):
    followers = get_followers(user_id)

    if not followers:
        print("No followers found for the given user.")
    else:
        print("Followers of user with ID", user_id)
        for follower in followers:
            print(follower)

        select_follower = input("Enter the ID of a follower to see their statistics or E to exit: ")
        if select_follower.isnumeric():
            select_follower  = int(select_follower)
            if select_follower != -1 and int(select_follower) in followers:
                following_count, followers_count = get_following_and_followers(select_follower)
                print(f"User {select_follower} follows {following_count} users and has {followers_count} followers.")

                all_tweets = get_all_tweets(select_follower)
                exit = False
                #show first three tweets
                start_index = 0
                end_index = min(start_index + 3, len(all_tweets))
                for i in range(start_index, end_index):
                    tweet = all_tweets[i]
                    print(f"Tweet ID: {tweet[0]}, Date: {tweet[1]}, Text: {tweet[2]}")
                    start_index += 3
                    
                while not exit:
                    choice = input("Options: F to follow, M for more Tweets, or B to go back to menu: ")
                    if choice.lower() == "f":
                        if not check_follow(user_id, select_follower):
                            cursor.execute("INSERT INTO follows (flwer, flwee, start_date) VALUES (?, ?, CURRENT_DATE)", (user_id, select_follower))
                            db_connection.commit()                
                            clear_screen()

                            print(f"User {user_id} is now following user {select_follower}.")
                            exit = True

                        else:
                            clear_screen()

                            print("Already following!")
                            exit = True

                    elif choice.lower() == "m":
                        if start_index < len(all_tweets):
                            print("Showing more tweets...")
                            # Display the next 3 tweets
                            end_index = min(start_index + 3, len(all_tweets))
                            for i in range(start_index, end_index):
                                tweet = all_tweets[i]
                                print(f"Tweet ID: {tweet[0]}, Date: {tweet[1]}, Text: {tweet[2]}")
                                start_index += 3
                    
                        else:
                            print("no more tweets")
                    elif choice.lower() == "b":
                        clear_screen()
                        print("Exiting.")
                        userMenu(user_id)
                    else:
                        print("Invalid choice.")
            else:
                print("Invalid follower ID")
        
        elif select_follower.lower()=='e':
            clear_screen()
            userMenu(user_id)
        else:
            print("Invalid follower ID")

def get_followers(usr):
    #Returns all the followers of usr
    #helper function for list_follower()

    cursor.execute("SELECT flwer FROM follows WHERE flwee = ?", (usr,))
    followers = cursor.fetchall()
    return [follower[0] for follower in followers]

def get_following_and_followers(usr):
    #Returns number of follower and following by usr
    #helper function for list_followers()
    cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ?", (usr,))
    followers_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM follows WHERE flwee = ?", (usr,))
    following_count = cursor.fetchone()[0]

    return followers_count, following_count

def get_all_tweets(user):
    #returns all the tweets written by user
    #helper function for list_followers
    cursor.execute("SELECT tid, tdate, text FROM tweets WHERE writer = ? ORDER BY tdate DESC", (user,))
    return cursor.fetchall()

def check_follow(user1, user2):
    #checks if user1 follows user2
    #helper function for list_followers
    #to avoid duplicates
    #returns true if user1 follows user2
    cursor.execute("SELECT COUNT(*) FROM follows WHERE flwer = ? AND flwee = ?", (user1, user2))
    count = cursor.fetchone()[0]

    if count > 0:
        return True  # user1 follows user2
    else:
        return False  # user1 does not follow user2
def get_tweet_stats(usr):
    current_user = usr
    while True:
        print('Please enter the tweet id that you wanna view:')
        tweet_id = input()
        try:
            # Try converting the input to an integer
            val = int(tweet_id)
            cursor.execute("SELECT * FROM tweets WHERE tid=?", (tweet_id,))
            tweet = cursor.fetchone()
            if tweet is None:
                print('Tweet ID does not exist')
            else:
                break

        except ValueError:
            # If conversion to integer fails, print a message and continue the loop
            print("The input is not an integer. Please try again.")


    cursor.execute("SELECT COUNT(*) FROM retweets WHERE tid=?", (tweet_id,))
    retweet_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tweets WHERE replyto=?", (tweet_id,))
    reply_count = cursor.fetchone()[0]

    print('The tweet statistics are listed below:\n')
    print(f"Tweet ID: {tweet[0]}")
    print(f"Writer: {tweet[1]}")
    print(f"Date: {tweet[2]}\n")
    print(f"Text: {tweet[3]}\n")
    print(f"Reply to: {tweet[4]}") if tweet[4] else print("Original Tweet (not a reply)")
    print(f"Number of Retweets: {retweet_count}")
    print(f"Number of Replies: {reply_count}\n")

    valid = False
    while not valid:
        print('Enter RP to reply to this tweet'  )
        print('Enter RT to retweet')
        print('Enter E to exit:'  )

        user_option = input().lower().strip()
        if user_option == 'rp':
            clear_screen()           
            compose_tweet(current_user, tweet_id)
            userMenu(usr)
        elif user_option =='rt':
            clear_screen()
            retweet(tweet_id,current_user)
            userMenu(usr)

        elif user_option =='e':
            clear_screen()
            userMenu(usr)

        else:
            print('Please enter rp/rt/exit only.')
    
def retweet(tweet_id, usr_id):
    # Check if the user has already retweeted this tweet
    cursor.execute("SELECT * FROM retweets WHERE usr = ? AND tid = ?", (usr_id, tweet_id))
    already_retweeted = cursor.fetchone()
    
    if already_retweeted:
        print('You have already retweeted this tweet.')
    else:
        cursor.execute("INSERT INTO retweets (usr, tid, rdate) VALUES (?, ?, datetime('now'))", (usr_id, tweet_id))
        db_connection.commit()
        print('Retweet successful!')

def clear_screen():
    # Check the OS and use the appropriate command to clear the terminal
    if os.name == 'posix':  # Linux and macOS
        os.system('clear')
    elif os.name == 'nt':  # Windows
        os.system('cls')
    else:
        # For other operating systems, a simple newline
        print('\n' * 100)

if __name__ == "__main__":
    main()
