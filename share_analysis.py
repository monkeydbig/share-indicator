import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import scipy.stats
stockcode = yf.download('MSFT',period='1y').reset_index()

#Trả về array giá trị max của mỗi rang ngày
def max_of_days(df,rang):
    array_high=[]
    for i in range(0,len(df)-rang):
        array_high.append(max(df['High'][i+1:i+rang+1]/df['Close'][i+1:i+rang+1]))
    return np.array(array_high)

#Trả về array giá trị min của mỗi rang ngày    
def min_of_days(df,rang):
    array_high=[]
    for i in range(0,len(df)-rang):
        array_high.append(min(df['Low'][i+1:i+1+rang]/df['Close'][i+1:i+1+rang]))
    return np.array(array_high) 

#Tính khoảng tin cậy
def m_c_i(df, confidence): #mean_confidence_interval
    a = np.array(df)
    n = len(a)
    m, std = np.mean(a),a.std()
    h = std * scipy.stats.t.ppf((1 + confidence) / 2, n-1)
    return m-h,m+h

#tính khoảng tin cậy của giá High 
def con_in_maxHigh(df,rang,confidence): 
    array=[]
    index=[]
    for i in confidence:
        x=max_of_days(df,rang)
        array.append(m_c_i(x,i))
        index.append(f'{i}'[2]+'0%')
    return pd.DataFrame(array,columns=('lowerbound_of_High','upperbound_of_High'),index=index)

#tính khoảng tin cậy của giá Low
def con_in_minLow(df,rang,confidence): 
    array=[]
    index=[]
    for i in confidence:
        x=min_of_days(df,rang)
        array.append(m_c_i(x,i))
        index.append(f'{i}'[2]+'0%')
    return pd.DataFrame(array,columns=('lowerbound_of_Low','upperbound_of_Low'),index=index)

#hàm tính điểm giao nhau
def intersect(df,data1,data2,check_range,threshold,price_check_range): #df ở đây là giá trị của hàm Macd
    
    riseordive=[]
    days=[]
    risedays=[]
    divedays=[]
    for k in range(check_range,len(df)-check_range):
        if data1[k-check_range] < data2[k-check_range]*(1-threshold) and data1[k+check_range] > data2[k+check_range]*(1+threshold): 
            riseordive.append('rise')
            days.append(df['Date'][k])
            risedays.append(df['Date'][k])
        elif data1[k-check_range] > data2[k-check_range]*(1+threshold) and data1[k+check_range] < data2[k+check_range]*(1-threshold):
            riseordive.append('dive')
            days.append(df['Date'][k])
            divedays.append(df['Date'][k])
        else:
            pass
    
    rise=[]
    for i in range(0,len(stockcode)-price_check_range):
        if stockcode['Date'][i] in (np.array(risedays)): 
            x=0
            for y in range(i+1,i+1+price_check_range):
                if stockcode['Close'][y]>stockcode['Close'][i]:
                    x+=1
                elif stockcode['Close'][y]<stockcode['Close'][i]:
                    pass
            if x==price_check_range:
                rise.append('risetrue')    
            elif x!=price_check_range:
                rise.append('risefalse')  
        elif stockcode['Date'][i] in (np.array(divedays)): 
            x=0
            for y in range(i+1,i+1+price_check_range):
                if stockcode['Close'][y]<stockcode['Close'][i]:
                    x+=1
                elif stockcode['Close'][y]>stockcode['Close'][i]:
                    pass
            if x==price_check_range:
                rise.append('divetrue') 
            elif x!=price_check_range:
                rise.append('divefalse')
        else:
            pass       
    return riseordive,days,rise


class stock_analysis():
    def __init__(self,name):
        self.name=name
#Tính đường ma theo chu kỳ
    def ma_period(self,df,period):
        ma_period=[]  
        for i in range(period,len(df)):
            ma_period.append(sum(df['Close'][i-period:i])/period)
        df1=pd.DataFrame(ma_period,columns=[f'ma_period{period}'])
        df1['Close']=np.array(df['Close'][period:])
        return pd.merge(df,df1,how='inner',on='Close')

#Nếu muốn ghép 2 chu kỳ khác nhau vào 1 df thì làm cách dưới
#pd.merge(big.ma_period(stockcode,10),big.ma_period(stockcode,20),how='inner',on=['Date','Open','High','Low','Close','Adj Close','Volume'])       

#hàm tính khoảng tin cậy giá high , low
    def high_conf_inv(self,df,rang,confidence):
        return con_in_maxHigh(df,rang,confidence)
    def low_conf_inv(self,df,rang,confidence):
        return con_in_minLow(df,rang,confidence)
    def Macd(self,df):
        EMA26=[]
        EMA12=[]
        Macd=[]
        Signal=[]
        for i in range(26,len(df)):
            if i==26:
                x1=sum(df['Close'][0:26])/26
                EMA26.append(x1)
                x2=sum(df['Close'][14:26])/12
                EMA12.append(x2)
            else:
                x1=(df['Close'][i]-EMA26[-1])*(2/(26+1))+EMA26[-1]
                EMA26.append(x1)
                x2=(df['Close'][i]-EMA12[-1])*(2/(12+1))+EMA12[-1]
                EMA12.append(x2)
        for i in range(0,len(EMA26)): #có thể thay bằng EMA12 , nó là như nhau
            Macd.append(EMA12[i]-EMA26[i])
        for i in range(35,len(df)):
            y=9
            if i==35:
                x=sum(Macd[0:9])/9
                Signal.append(x)    
            else:
                x=(Macd[y]-Signal[-1])*(2/(9+1))+Signal[-1]
                y+=1
                Signal.append(x)
        data=pd.DataFrame([np.array(df['Date'][35:]),np.array(Signal),np.array(Macd)[9:],EMA26[9:],EMA12[9:]],['Date','Signal','Macd','EMA26','EMA12']).transpose()
        return pd.merge(df,data,how='inner',on='Date')
    def macd_check(self,df,check_range,threshold,price_check_range):
        x=intersect(share.Macd(df),share.Macd(df)['Macd'],share.Macd(df)['Signal'],check_range,threshold,price_check_range)[0]
        y=intersect(share.Macd(df),share.Macd(df)['Macd'],share.Macd(df)['Signal'],check_range,threshold,price_check_range)[1]
        z=intersect(share.Macd(df),share.Macd(df)['Macd'],share.Macd(df)['Signal'],check_range,threshold,price_check_range)[2]
        data=pd.DataFrame(x,columns=['r/dMacd'])
        data['Date']=y
        data1=pd.DataFrame(z,columns=['t/fMacd'])
        data1['Date']=y
        sum1=pd.merge(data,data1,how='inner',on='Date')
        sum2=pd.merge(sum1,stockcode,how='outer')
        return sum2
    def Bollinger(self,df,period,k): #N chu kỳ ngày #K hệ số của độ lệch chuẩn
        df['TP']=(df['Close']+df['High']+df['Low'])/3
        y=[]
        for i in range(period,len(df)):
            y.append(df['TP'][i-period:i].std())
        df1=pd.DataFrame(y,columns=[f'std_{period}'])
        df1['Date']=np.array(df['Date'][period:])
        ma_period=[]
        for i in range(period,len(df)):
            ma_period.append(sum(df['TP'][i-period:i])/period)
        df2=pd.DataFrame(ma_period,columns=[f'ma_period{period}'])
        df2['Date']=np.array(df['Date'][period:])
        x= pd.merge(df1,df2,how='inner',on='Date')
        z= pd.merge(df,x,how='inner',on='Date')
        z['upband']=z[f'ma_period{period}']+k*z[f'std_{period}']
        z['downband']=z[f'ma_period{period}']-k*z[f'std_{period}']
        z['distance']=z['upband']-z['downband']
        return z
    def trend_boll(self,df,rang): #df chỗ này là giá trị của hàm Bollinger
        day=[]
        for i in range(0,len(df)):
            day.append(df['Date'][i].day)
        df['day']=day

        x=[]
        for i in range(rang,len(df)):
            slope=np.polyfit(df['day'][i-rang:i],df['distance'][i-rang:i],1)
            x.append(slope[0])
        df1=pd.DataFrame(x,columns=['slope'])
        df1['Date']=np.array(df['Date'][rang:])
        df2=pd.merge(df1,df,how='inner',on='Date')

        y=[]
        for i in range(0,len(df2)):
            if df2['slope'][i]>(1.1):
                y.append('widen')
            elif df2['slope'][i]<(0.9):
                y.append('narrow')
            else:
                y.append('')

        return df2
    
