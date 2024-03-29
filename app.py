import streamlit as st
import preprocessor
from urlextract import URLExtract
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud,STOPWORDS
from collections import Counter
import seaborn as sns
import datetime
from PIL import Image
import gspread
import sentiment
try:
    import emojis
except:
    pass
#function

def emoji_analyse(selected_user,df):
    emoji_list = []
    for msg in df['message']:
        e = emojis.get(msg)
        if e != set():
            emoji_list.extend(e)
    if len(emoji_list)>0:
        emoji_df=pd.DataFrame.from_dict(Counter(emoji_list),orient='index').reset_index()
        emoji_df = emoji_df.sort_values(by=[0], ascending=False).reset_index()
        emoji_df.rename(columns={'index':"Emojis",0:"Count"},inplace=True)
        emoji_df=emoji_df.drop(['level_0'], axis=1)
        print(emoji_df)
        return emoji_df
    else:
        emoji_df=pd.DataFrame(columns=['Emojis'])
        return emoji_df

def helper(selected_user,df):

    num_msg = df.shape[0]
    words = []
    emoji_list=emoji_analyse(selected_user,df)
    emoji_unique=emoji_list['Emojis'].unique()
    adder=''
    temp_alp=[]
    for word in df['message']:

        for alp in word:
            if alp not in emoji_unique:
                adder+=alp
            else:
                words.append(alp)
        temp_alp.append(adder)
        adder=''

        words.extend(temp_alp[0].split())
        temp_alp=[]
    msg_count = len(words)

    count = df[df['message'] == '<Media omitted>\n'].shape[0]

    extractor=URLExtract()
    links=[]
    for msg in df['message']:
        links.extend(extractor.find_urls(msg))
    count_links=len(links)

    return num_msg,msg_count,count,count_links

#wordcloud funtion
def create_wordcloud(selected_user,df):
    stopwords=set(STOPWORDS)
    df = df[df['message'] != '<Media omitted>\n']
    df = df[df['message'] != 'Waiting for this message']
    df = df[df['message'] != 'This message was deleted']
    wc=WordCloud(width=500,height=500,stopwords=stopwords,min_font_size=10,background_color='white')
    df_wc=wc.generate(df.message.str.cat(sep=' '))
    return df_wc

#top 20 most use words
def most_used_words(selected_user,df):
    new_df = df[df['users'] != 'group_notification']
    new_df = new_df[new_df['message'] != '<Media omitted>\n']
    new_df = new_df[new_df['message'] != 'Waiting for this message']
    new_df = new_df[new_df['message'] != 'This message was deleted']

    words = []
    list1=set(STOPWORDS)
    emoji_list=emoji_analyse(selected_user,df)
    emoji_unique = emoji_list['Emojis'].unique()
    temp_alp=[]
    adder=''
    final_words=[]

    for msg in new_df['message']:
        for word in msg:
            if word not in emoji_unique:
                adder+=word

        temp_alp.append(adder)
        adder = ''
        words.extend(temp_alp[0].split())
        temp_alp = []

    for i in words:
        if i not in list1:
            final_words.append(i)
    count_df = pd.DataFrame(Counter(final_words).most_common(20))
    if len(count_df)>0:
        count_df = count_df.rename(columns={0: 'Words', 1: 'Count'})
    else:
        count_df=pd.DataFrame(columns=['Words','Count'])


    return count_df
def monthly_active(selected_user,df):
    df['month_num'] = df['date'].dt.month
    timeline = df.groupby(['year', 'month']).count()['message'].reset_index()
    return timeline



def day_analysis(selected_user,df):
    new_df = pd.DataFrame(df.groupby(['day_name']).count()['message'].reset_index())
    list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    list1 = []
    for i in list:
        for index, row in new_df.iterrows():
            if row['day_name'] == i:
                list1.append([i, row['message']])
    new1_df = pd.DataFrame(list1)
    new1_df.rename(columns={0: 'Day Name', 1: 'Count'}, inplace=True)
    return new1_df

def heatmap(selected_user,df):
    activity_heatmap=df.pivot_table(index='day_name', columns='hour_range', values='message', aggfunc='count').fillna(0)
    return activity_heatmap

st.sidebar.title("Whatsapp Chat Analyzer")
st.sidebar.write('This is a whatsapp chat analyzer which will help you to find the insights from your convertation with other.. Are you excited!!')
st.sidebar.write("Your data will not be saved... We respect your privacy")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    data=bytes_data.decode("utf-8")
    if data[15:17]=='PM' or data[15:17]=='AM' or data[16:18]=='AM' or data[16:18]=='PM':
        df=preprocessor.preprocess1(data)
    else:
        df=preprocessor.preprocess(data)



    #fetch unique user
    users_list=df.users.unique().tolist()
    try:
        users_list.remove('group_notification')
    except:
        pass
    users_list.sort()
    users_list.insert(0,"Overall")
    selected_user=st.sidebar.selectbox("Show analysis wrt: ",users_list)
    a = df.year.unique().tolist()
    a.insert(0,"Overall")
    start_year = st.sidebar.selectbox("Pick the year", a)

    if start_year!='Overall':
        df = df[df['year'] == start_year]
        b = df.month_num.unique().tolist()
        start_month = st.sidebar.selectbox("Pick the month", b)

        df = df[df['month_num'] == start_month]
        c=df.day.unique().tolist()
        c.insert(0,"Overall")
        specific_date=st.sidebar.selectbox("Pick the date",c)
        if specific_date != 'Overall':
            df=df[df['day']==specific_date]
    if selected_user!='Overall':
        df=df[df['users'] == selected_user]


    if st.sidebar.button("Show Analysis"):
        #Stats area
        num_msg,msg_count,media_count,count_links=helper(selected_user,df)
        col1,col2,col3,col4=st.columns(4)

        with col1:
            st.title("Total Messages")
            st.header(num_msg)

        with col2:
            st.title("Word Count")
            st.header(msg_count)

        with col3:
            st.title("Media Shared")
            st.header(media_count)

        with col4:
            st.title("Link_shared count")
            st.header(count_links)

        if num_msg==0:
            st.error("No Data")
        else:

            #finding the busiest user in the group(group level)
            if selected_user=='Overall':
                st.title("Most busy users")

                col1,col2=st.columns(2)
                busy = df.users.value_counts().head()
                fig, ax = plt.subplots()



                with col1:

                    ax.barh(busy.index, busy.values)
                    for index, value in enumerate(busy.values):
                        plt.text(value, index, str(value))
                    #plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    busy1 = df.users.value_counts()
                    percent_of_busyness = []
                    y = df.users.value_counts().sum()
                    for value in busy1.values:
                        val=(value / y) * 100
                        percent_of_busyness.append(round(val,2))

                    #busy_df=round(df.users.value_counts()/df.shape[0])*100,2)

                    busy_df = pd.DataFrame({'Name': busy1.index, '% of chat': percent_of_busyness})
                    st.dataframe(busy_df)

            #Most 20 words
            st.title("Most used 20 words")
            most_words_df = most_used_words(selected_user, df)
            col1, col2 = st.columns(2)
            fig, ax = plt.subplots()
            with col1:
                st.header('Data')
                st.dataframe(most_words_df)
            with col2:
                st.header("Visual Analysis")
                x = most_words_df['Words']
                y = most_words_df['Count']
                ax.bar(x, y, color='r')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            #Emoji
            st.title("Emoji")
            emoji_df = emoji_analyse(selected_user, df)
            emoji_df=emoji_df.drop(emoji_df.index[20:len(emoji_df['Emojis'])])
            col1, col2 = st.columns(2)
            fig, ax = plt.subplots()
            with col1:
                st.header('Emoji_Data')
                st.dataframe(emoji_df)
            with col2:
               pass
            col1,col2=st.columns(2)
            with col1:
                st.title('Monthly Activity')
                time_df=monthly_active(selected_user,df)
                time = []
                for i in range(time_df.shape[0]):
                    time.append(time_df['month'][i] + ' ' + str(time_df['year'][i]))
                message_count = time_df['message']
                fig,ax=plt.subplots()
                ax.scatter(time,message_count)
                ax.plot(time,message_count)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.title('Daily Activity')
                day_df = day_analysis(selected_user, df)
                fig,ax=plt.subplots()
                ax.plot(day_df['Day Name'],day_df['Count'])
                plt.xticks(rotation='vertical')
                st.pyplot(fig)


            #heatmap
            st.header('See when its perfect time to talk')
            fig,ax=plt.subplots(figsize=(10,5))
            pivot_df=heatmap(selected_user,df)
            ax=sns.heatmap(pivot_df)
            st.pyplot(fig)




            #WordCloud

            st.title("Word Cloud")
            df_wc=create_wordcloud(selected_user,df)
            fig,ax=plt.subplots()
            ax.imshow(df_wc)
            plt.axis('off')
            st.pyplot(fig)

            # sentiment
            st.title('Sentiment Analysis')
            emotion_df = sentiment.sentiment_score(df)
            emotion_df = emotion_df.reset_index()
            for index, row in emotion_df.iterrows():
                st.subheader(row['users'] +" "+ row['emotion'])
            emotion_df=emotion_df[['users','compound','status']]
            emotion_df=emotion_df.rename(columns={'compound': 'Sentiment'})
            st.dataframe(emotion_df)
            if len(emotion_df)==2:
                emotion_df=emotion_df.sort_values(by=['Sentiment'],ascending=False)
                emotion_df=emotion_df.reset_index()
                print(emotion_df)
                percentage=((emotion_df.loc[0,'Sentiment']-emotion_df.loc[1,'Sentiment'])/emotion_df.loc[1,'Sentiment'])*100
                percentage=round(percentage,2)
                statement='User '+str(emotion_df['users'][0])+' is more positive than User '+ str(emotion_df['users'][1])+ ' by '+ str(percentage)+'%.'
                st.text(statement)


    name=st.sidebar.text_input("Enter you name")
    feedbacks=st.sidebar.text_area("Please enter your feedback about the website")
    if st.sidebar.button("Submit"):
        sa = gspread.service_account(filename='feedbacks-368005-cba6d4b54093.json')
        sh = sa.open('Feedbacks')

        wks = sh.worksheet('Sheet1')

        wks.insert_row([name,feedbacks], wks.row_count)
        st.markdown("Thank You for your feedback")
st.sidebar.subheader("Created by Paul")
