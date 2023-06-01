import requests
import csv
# Define the CSV file path
csv_file = "tweets.csv" #Example
def collect(csv_file):
    # Set up the authorization headers with the bearer token
    headers = {
        "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
    }

    # Send a POST request to activate the guest token
    response = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers=headers)
    guest_token = response.json()["guest_token"]

    # Add the guest token to the headers for subsequent requests
    headers["x-guest-token"] = guest_token

    # Set up the request parameters
    url = "https://api.twitter.com/1.1/search/tweets.json"
    query = "Squid Game"
    count = 100
    lang = "en"



    # Open the CSV file for writing
    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Tweet ID", "Timestamp", "Text", "User", "Hashtags", "Retweets", "Likes", 
            "Followers", "Friends", "URLs", "Media", "Location", "Retweeted", "In Response To"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        max_id = None
        total_responses = 0
        page = 1

        while total_responses < 10000:  # Fetch responses until the desired count is reached
            params = {
                "q": query,
                "result_type": "recent",
                "count": count,
                "lang": lang,
                "max_id": max_id,
                "tweet_mode": "extended"
            }

            # Send a GET request to the Twitter search endpoint
            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            if "statuses" not in data:
                break

            tweets = data["statuses"]

            for tweet in tweets:
                tweet_id = tweet["id_str"]
                timestamp = tweet["created_at"]
                tweet_text = tweet["full_text"]
                tweet_user = tweet["user"]["screen_name"]
                hashtags = [tag["text"] for tag in tweet["entities"]["hashtags"]]
                retweet_count = tweet["retweet_count"]
                favorite_count = tweet["favorite_count"]
                user_followers = tweet["user"]["followers_count"]
                user_friends = tweet["user"]["friends_count"]
                urls = [url["expanded_url"] for url in tweet["entities"]["urls"]]
                media = [media["media_url"] for media in tweet["entities"].get("media", [])]
                location = tweet["user"]["location"]
                is_retweeted = tweet["retweeted"]
                in_response_to = tweet["in_reply_to_status_id_str"]

                # Write the tweet information as a row in the CSV file
                writer.writerow({
                    "Tweet ID": tweet_id,
                    "Timestamp": timestamp,
                    "Text": tweet_text,
                    "User": tweet_user,
                    "Hashtags": ", ".join(hashtags),
                    "Retweets": retweet_count,
                    "Likes": favorite_count,
                    "Followers": user_followers,
                    "Friends": user_friends,
                    "URLs": ", ".join(urls),
                    "Media": ", ".join(media),
                    "Location": location,
                    "Retweeted": is_retweeted,
                    "In Response To": in_response_to
                })

                total_responses += 1
                if total_responses >= 10000:
                    break

            if len(tweets) == 0:
                break

            max_id = str(int(tweets[-1]["id_str"]) - 1)

            page += 1

