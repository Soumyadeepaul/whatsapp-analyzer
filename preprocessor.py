import re
import pandas as pd
def preprocess(data):
    #pattern of regex this one is for time and date
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    #spliting it into messages and dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    #creating a dataframe df with 2 columns
    df = pd.DataFrame({'user_message': messages, 'date': dates})
    #converting date time into proper formate using to_datetime function
    try:
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %H:%M - ')
    except:
        try:
            df['date'] = pd.to_datetime(df['date'], format='%d/%m/%y, %H:%M - ')
        except:
            try:
                df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y, %H:%M - ')
            except:
                df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y, %H:%M - ')
    # seperate user and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['users'] = users
    df['message'] = messages
    #droping the column
    df.drop('user_message',axis=1,inplace=True)

    #making new column accordingly
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = df.date.dt.hour
    df['minute'] = df.date.dt.minute
    df['day_name'] = df['date'].dt.day_name()
    hour_range = []
    for i in range(df.shape[0]):
        if df['hour'][i]==23:
            hour_range.append(str(df['hour'][i]) + '-' + str('0'))
        else:
            hour_range.append(str(df['hour'][i]) + '-' + str(df['hour'][i] + 1))
    df['hour_range'] = hour_range
    return(df)
def preprocess1(data):
    # pattern of regex this one is for time and date
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[AP][M]\s-\s'
    # spliting it into messages and dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    dates2 = []
    for i in dates:
        dates2.append(i.split(','))

    def convert24(str1):
        if str1[7:9] == 'AM' and str1[1:3] == '12':
            return '00' + str1[3:7]
        elif str1[7:9] == 'AM':
            return str1[1:-5]
        elif str1[7:9] == 'PM' and str1[1:3] == '12':
            return str1[1:7]
        elif str1[6:8] == 'AM':
            return '0' + str1[1:-5]

        elif str1[6:8] == 'PM':
            return str(int(str1[1:2]) + 12) + str1[2:6]
        else:
            return str(int(str1[1:3]) + 12) + str1[3:7]

    for i in range(len(dates2)):
        dates2[i][1] = convert24(dates2[i][1])
    dates3 = []
    for i in dates2:
        dates3.append(i[0] + ', ' + i[1] + '- ')

    # creating a dataframe df with 2 columns
    df = pd.DataFrame({'user_message': messages, 'date': dates3})
    # converting date time into proper formate using to_datetime function
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y, %H:%M - ')

    # seperate user and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['users'] = users
    df['message'] = messages
    # droping the column
    df.drop('user_message', axis=1, inplace=True)

    # making new column accordingly
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num']=df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = df.date.dt.hour
    df['minute'] = df.date.dt.minute
    df['day_name'] = df['date'].dt.day_name()
    hour_range = []
    for i in range(df.shape[0]):
        if df['hour'][i] == 23:
            hour_range.append(str(df['hour'][i]) + '-' + str('0'))
        else:
            hour_range.append(str(df['hour'][i]) + '-' + str((df['hour'][i]) + 1))
    df['hour_range'] = hour_range
    return(df)
