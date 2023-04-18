from wordcloud import STOPWORDS
import string
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm
def sentiment_score(df):
    df = df[df['users'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>\n']
    df = df[df['message'] != 'Waiting for this message']
    df = df[df['message'] != 'This message was deleted']
    sia = SentimentIntensityAnalyzer()
    for index, row in df.iterrows():
        i = row['message'].lower()
        i = i[:-2].translate(str.maketrans('', '', string.punctuation))
        final = []
        token = i.split()
        for i in token:
            if i not in STOPWORDS:
                final.append(i)
        final = ' '.join(final)
        score = sia.polarity_scores(final)
        df.loc[index, 'positive'] = [score['pos']]
        df.loc[index, 'neutral'] = [score['neu']]
        df.loc[index, 'negative'] = [score['neg']]
        df.loc[index, 'compound'] = [score['compound']]
        df.loc[index, 'score'] = [score]
    new_df=df.groupby('users').mean()
    for index,row in new_df.iterrows():
        if row['compound']>0.7 :
            new_df.loc[index,'emotion']='\U0001F601'
            new_df.loc[index, 'status'] = 'Very Positive'
        elif row['compound']>0.5 :
            new_df.loc[index,'emotion']='\U0001F604'
            new_df.loc[index, 'status'] = 'Positive'
        elif row['compound']>0.3 :
            new_df.loc[index,'emotion']='\U0001F600'
            new_df.loc[index, 'status'] = 'Positive'
        elif row['compound']>0.05 :
            new_df.loc[index,'emotion']='\U0001F60A'
            new_df.loc[index, 'status'] = 'Just Positive'
        elif row['compound']<-0.7 :
            new_df.loc[index,'emotion']='\U0001F62D'
            new_df.loc[index, 'status'] = 'Very Negative'
        elif row['compound']<-0.5 :
            new_df.loc[index,'emotion']='\U0001F625'
            new_df.loc[index, 'status'] = 'Negative'
        elif row['compound']<-0.3 :
            new_df.loc[index,'emotion']='\U0001F61E'
            new_df.loc[index, 'status'] = 'Negative'
        elif row['compound']<-0.05 :
            new_df.loc[index,'emotion']='\U0001F62B'
            new_df.loc[index, 'status'] = 'Just Negative'
        else:
            new_df.loc[index, 'emotion'] = '\U0001F642'
            new_df.loc[index, 'status'] = 'Neutral'
    return new_df
