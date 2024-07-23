import pandas as pd
import csv
from googleapiclient.discovery import build
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
API_KEY="AIzaSyBBpItOOYYUZL3W7FXkMMuoe6G5gbey9kg"
youtube = build('youtube', 'v3', developerKey=API_KEY)
topic = 'product videos'
max_results = 100
video_links = []
next_page_token = None

while len(video_links) < max_results:
    search_response = youtube.search().list(
        q=topic,
        type='video',
        part='id',
        maxResults=min(50, max_results - len(video_links)),  # Request up to 50 videos
        pageToken=next_page_token
    ).execute()

    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        video_link = f'https://www.youtube.com/watch?v={video_id}'
        video_links.append(video_link)

    next_page_token = search_response.get('nextPageToken')
    if next_page_token is None:
        break
csv_file = 'product_videos.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['Video Links'])
    csv_writer.writerows([[link] for link in video_links])

print(f'{len(video_links)} video links saved to {csv_file}')
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
# Read video links from the CSV file
video_links = []
with open('product_videos.csv', 'r', newline='', encoding='utf-8') as f:
    csv_reader = csv.reader(f)
    next(csv_reader)  # Skip the header row
    for row in csv_reader:
        video_links.append(row[0])
comments_data = []
for video_link in video_links:
    video_id = video_link.split('=')[-1]

    try:
        video_request = youtube.videos().list(
            part="snippet",
            id=video_id,
        )
        video_response = video_request.execute()
        if video_response.get('items'):
            video_title = video_response['items'][0]['snippet']['title']
            channel_id = video_response['items'][0]['snippet']['channelId']

            channel_request = youtube.channels().list(
                part="snippet",
                id=channel_id,
            )
            channel_response = channel_request.execute()

            if channel_response.get('items'):
                channel_name = channel_response['items'][0]['snippet']['title']

                comment_request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                )
                comment_response = comment_request.execute()


        for item in comment_response.get('items', []):
              snippet = item['snippet']
              comment = snippet['topLevelComment']['snippet']['textDisplay']
              like_count = snippet['topLevelComment']['snippet']['likeCount']
              reply_count = snippet['totalReplyCount']
              commented_date = snippet['topLevelComment']['snippet']['publishedAt']
              # video_id = snippet['videoId']

              comments_data.append([video_id, video_title,channel_name, comment, like_count, reply_count, commented_date])

    except Exception as e:
        if 'commentsDisabled' in str(e):
            print(f"Comments disabled for video {video_id}")
        else:
            print(f"Error fetching comments for video {video_id}: {str(e)}")
csv_file = 'comment_info.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(['video Id','Video Name','Channel','Comment', 'Like Count', 'Reply Count', 'Commented Date'])
    csv_writer.writerows(comments_data)

print(f'{len(comments_data)} comments with additional info saved to {csv_file}')

def sentiment_scores(comment, polarity):
    # Creating a SentimentIntensityAnalyzer object.
    sentiment_object = SentimentIntensityAnalyzer()
    sentiment_dict = sentiment_object.polarity_scores(comment)
    polarity.append(sentiment_dict['compound'])
    return polarity

polarity = []
positive_comments = []
negative_comments = []
neutral_comments = []

csv_file = "comment_info.csv"

try:
    with open(csv_file, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        print("Analysing Comments...")
        for row in reader:
            comment = row['Comment']
            polarity = sentiment_scores(comment, polarity)

            if polarity[-1] > 0.05:
                positive_comments.append(row)
            elif polarity[-1] < -0.05:
                negative_comments.append(row)
            else:
                neutral_comments.append(row)

    # Print first 5 polarity scores
    print(polarity[:5])

    # Print counts of each type of comments
    print(f"Positive comments: {len(positive_comments)}")
    print(f"Negative comments: {len(negative_comments)}")
    print(f"Neutral comments: {len(neutral_comments)}")

except PermissionError:
    print(f"Permission denied: Unable to access the file '{csv_file}'. Please check the file permissions.")
except FileNotFoundError:
    print(f"The file '{csv_file}' was not found. Please check the file path.")
except Exception as e:
    print(f"An error occurred: {e}")
