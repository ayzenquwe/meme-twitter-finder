from pathlib import Path
import divsufsort as sa
import ctypes

SIMILARITY_THRESHOLD = 20


def get_tweet(data, index):
    return (get_tweet_header_bytes(data, index) + get_tweet_ending_bytes(data, index)).decode("UTF-8")


def get_tweet_ending(data, index):
    return get_tweet_ending_bytes(data, index).decode("UTF-8")


def get_tweet_header_bytes(data, index):
    return data[data.rfind(0x01, 0, index)+1:index]


def get_tweet_ending_bytes(data, index):
    return data[index:data.find(0x01, index, len(data))]


def process_data(data, res):
    tweets = {}
    tweet_template = get_tweet_ending(data, res[0])
    tweet_similarity = 0

    for i in range(1, len(data)):
        try:
            sim = similarity(tweet_template, get_tweet_ending(data, res[i]))
            if sim >= SIMILARITY_THRESHOLD:
                tweet_similarity += sim
            else:
                if tweet_similarity >= SIMILARITY_THRESHOLD * 100:
                    tweet = get_tweet(data, res[i-1])
                    tweets[tweet] = max(tweets[tweet], tweet_similarity) if tweet in tweets else tweet_similarity

                tweet_template = get_tweet_ending(data, res[i])
                tweet_similarity = 0
        except:
            continue

    return tweets


def similarity(str1, str2):
    result = 0
    for i in range(min(len(str1), len(str2))):
        if str1[i] != str2[i]:
            break
        result += 1

    return result


def display_results(tweets):
    with open('results', 'w') as result_file:
        for k, v in sorted(tweets.items(), key=lambda x: x[1], reverse=True):
            result_file.write("--------------------------------\n")
            result_file.write("Similarity rank: %d\n\n" % v)
            result_file.write("%s\n\n" % k)


data = Path("data").read_text().encode('UTF-8')

res = (ctypes.c_int * len(data))()
sa.divsufsort(data, res)

display_results(process_data(data, res))
