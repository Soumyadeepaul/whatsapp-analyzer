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
import urllib.request
#function
def helper(selected_user,df):
    if selected_user!='Overall':
        df=df[df['users'] == selected_user]
    num_msg = df.shape[0]
    words = []
    for msg in df['message']:
        words.extend(msg.split())
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
    if selected_user!='Overall':
        df=df[df.users==selected_user]
    stopwords=set(STOPWORDS)
    df = df[df['message'] != '<Media omitted>\n']
    df = df[df['message'] != 'Waiting for this message']
    df = df[df['message'] != 'This message was deleted']
    wc=WordCloud(width=500,height=500,stopwords=stopwords,min_font_size=10,background_color='white')
    df_wc=wc.generate(df.message.str.cat(sep=' '))
    return df_wc

#top 20 most use words
def most_used_words(selected_user,df):
    if selected_user!='Overall':
        df=df[df['users'] == selected_user]
    new_df = df[df['users'] != 'group_notification']
    new_df = new_df[new_df['message'] != '<Media omitted>\n']
    new_df = new_df[new_df['message'] != 'Waiting for this message']
    new_df = new_df[new_df['message'] != 'This message was deleted']

    words = []
    list1=set(STOPWORDS)
    for msg in new_df['message']:
        for word in msg.lower().split():
            if word not in list1:
                words.append(word)

    count_df = pd.DataFrame(Counter(words).most_common(20))
    count_df = count_df.rename(columns={0: 'Words', 1: 'Count'})

    return count_df
def monthly_active(selected_user,df):
    if selected_user!='Overall':
        df=df[df['users'] == selected_user]
    df['month_num'] = df['date'].dt.month
    timeline = df.groupby(['year', 'month']).count()['message'].reset_index()
    return timeline



#def emoji_analyse(selected_user,df):
#    if selected_user!='Overall':
#        df=df[df['users'] == selected_user]
#   emojis=[]
#   for msg in df['message']:
#       emojis.extend([c for c in msg if c in emoji.UNICODE_EMOJI['en']])
#   emoji_df=pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
#    return emoji_df

def day_analysis(selected_user,df):
    if selected_user!='Overall':
        df=df[df['users'] == selected_user]

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
    if selected_user!='Overall':
        df=df[df['users'] == selected_user]
    activity_heatmap=df.pivot_table(index='day_name', columns='hour_range', values='message', aggfunc='count').fillna(0)
    return activity_heatmap
urllib.request.urlretrieve('data:image/jpg;base64,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','whats.png')
image=Image.open('whats.png ')
st.sidebar.image(image)
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
    users_list.remove('group_notification')
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
            #st.title("Emoji")
            #emoji_df = emoji_analyse(selected_user, df)
            #col1, col2 = st.columns(2)
            #fig, ax = plt.subplots()
            #with col1:
            #    st.header('Emoji_Data')
            #    st.dataframe(emoji_df)
            #with col2:
            #   pass
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
    name=st.sidebar.text_input("Enter you name")
    feedbacks=st.sidebar.text_area("Please enter your feedback about the website")
    if st.sidebar.button("Submit"):
        sa = gspread.service_account(filename='feedbacks-368005-cba6d4b54093.json')
        sh = sa.open('Feedbacks')

        wks = sh.worksheet('Sheet1')

        wks.insert_row([name,feedbacks], wks.row_count)
        st.markdown("Thank You for your feedback")
st.sidebar.subheader("Created by Paul")



