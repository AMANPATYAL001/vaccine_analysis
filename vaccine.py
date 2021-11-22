import streamlit as st
from fpdf import FPDF
import pandas as pd
import base64
import plotly.graph_objects as go
import plotly.express as px
url_world='https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'
url_us_states='https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv'

@st.cache(allow_output_mutation=True)
def data_sets(url_world,url_us_states):
    df=pd.read_csv(url_world,usecols=['location','iso_code','date','people_fully_vaccinated','daily_vaccinations_per_million','daily_vaccinations','total_vaccinations'])
    us=pd.read_csv(url_us_states,usecols=['location','date','people_fully_vaccinated','daily_vaccinations_per_million','daily_vaccinations','total_vaccinations'])
    return df,us
df,us=data_sets(url_world,url_us_states)
st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 1000px;
        padding-top: 5 px;
        padding-right: 5 px;
        padding-left: 5 px;
        padding-bottom: 50 px;
    }}
</style>
""",
        unsafe_allow_html=True,
    )

st.title('Vaccination Drive across Countries and US states')
st.subheader('Random rows of the Dataset') 
st.dataframe(df.sample(6),1000,200)

##### world animation map plot #####
df.rename(columns={'location':'country'},inplace=True)
d=df.groupby('country').agg({'date':'max','iso_code':'last','total_vaccinations':'last',
                           'daily_vaccinations_per_million':'last',
                           'daily_vaccinations':'last',
                           'people_fully_vaccinated':'last'}).reset_index()

d = df.sort_values(by='date') 
d['timestamp'] = d.date.astype(str)
map_op=['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance', 'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg', 'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl', 'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric', 'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys', 'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet', 'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges', 'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl', 'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn', 'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu', 'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar', 'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn', 'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid', 'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr', 'ylorrd']
sel_map_color=st.selectbox('Pick a theme ', map_op,1)
st.subheader('Datewise Drive across the World (Interactive)')
@st.cache
def world_ani(sel_map_color):
    fig = px.choropleth(d.dropna(), locations="country",color_continuous_scale=sel_map_color,
                        color="people_fully_vaccinated", 
                        hover_data=["country",'daily_vaccinations','date','daily_vaccinations_per_million','people_fully_vaccinated'],height=500, width=1000,
                        locationmode = 'country names',
                        animation_frame="timestamp")
    return fig
    
st.plotly_chart(world_ani(sel_map_color))
##### world animation map plot #####

#### seven nation's area chart ####
c=df.dropna(subset=['people_fully_vaccinated'],axis=0).query('country == "India" or country == "United States" or country == "Australia" or country == "England" or country == "Russia" or country == "New Zealand" or country == "Canada"')
st.subheader('Seven Countries People fully Vaccinated Progress Graph')
left_column, right_column = st.columns(2)
@st.cache
def seven_area():
    fig_seven_nations = px.area(pd.crosstab(index=c.date,columns=c.country,values=c.people_fully_vaccinated,aggfunc='sum'),
                facet_col="country", facet_col_wrap=2,facet_row_spacing=0.1,
                facet_col_spacing=0.06, 
                height=600, width=492,template='plotly_dark')
    fig_seven_nations.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig_seven_nations.update_yaxes(showticklabels=True)
    #fig_seven_nations.write_image('res/fig_seven_nations.png')
    return fig_seven_nations
with left_column:
    st.plotly_chart(seven_area())
#### seven nation's area chart ####

#### seven nation's line chart ####
# st.subheader('Same as Before (Line Chart)')
@st.cache
def seven_line():
    fig_seven_nations_line=px.line(c, x="date", y='total_vaccinations',
                hover_data={"date": "|%B %d, %Y"},color="country")
    fig_seven_nations_line.update_xaxes(
        rangeslider_visible=True,
        tickformatstops = [
            dict(dtickrange=[86400000, 604800000], value="%e.%b d"),
            dict(dtickrange=[604800000, "M1"], value="%e.%b "),
            dict(dtickrange=["M1", "M12"], value="%b '%y M"),
            dict(dtickrange=["M12", None], value="%Y Y")
        ]
    )
    draft_template = go.layout.Template()
    draft_template.layout.annotations = [
        dict(
            name='aman',
            text="SARS-CoV-2",
            textangle=-25,
            opacity=0.2,
            font=dict(color="black", size=30),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.6,
            showarrow=False,
        )
    ]
    fig_seven_nations_line.update_layout(template=draft_template,height=450, width=500,margin=dict(
        l=60,
        r=0,
        b=15,
        t=15,
        pad=4
    ))
    #fig_seven_nations_line.write_image('res/fig_seven_nations_line.png')
    return fig_seven_nations_line
with right_column:
    st.plotly_chart(seven_line())
#### seven nation's line chart ####


##### us animation map ######
us.drop(us.loc[us.location=='United States'].index,inplace=True)
states = {
        'AK': 'Alaska','AL': 'Alabama',
        'AR': 'Arkansas','AS': 'American Samoa','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut',
        'DC': 'District of Columbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia',
        'GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho',
        'IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine',
        'MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri', 'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi','MT': 'Montana',
        'NA': 'National','NC': 'North Carolina','ND': 'North Dakota','NE': 'Nebraska','NH': 'New Hampshire','NJ': 'New Jersey',
        'NM': 'New Mexico','NV': 'Nevada','NY': 'New York','OH': 'Ohio',
        'OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'Puerto Rico','RI': 'Rhode Island',
        'SC': 'South Carolina','SD': 'South Dakota','TN': 'Tennessee', 'TX': 'Texas',
        'UT': 'Utah','VA': 'Virginia','VI': 'Virgin Islands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin',
        'WV': 'West Virginia','WY': 'Wyoming'
}
sta=pd.DataFrame.from_dict(states, orient='index').reset_index().rename(columns={'index':'code',0:'name'})
uss=us.merge(sta,left_on='location',right_on='name',how='outer').dropna(subset=['date','location'],axis=0)
uss=uss.sort_values(by='date')
uss['timestamp'] = uss.date.astype(str)
uss['text'] = uss['location'] + '<br>'+   uss['timestamp'] +'<br>'+\
' daily_vaccinations_per_million :' + uss['daily_vaccinations_per_million'].astype(str)
st.subheader('Datewise Analysis of US states Aman')
@st.cache
def us_ani(allow_output_mutation=True):
    fig_us_map = px.choropleth(uss.dropna(), locations="code",
                        color="people_fully_vaccinated",
                        hover_data=["location",'total_vaccinations','daily_vaccinations_per_million','people_fully_vaccinated'],
                        color_continuous_scale=px.colors.sequential.Plasma,
                        locationmode = 'USA-states',scope="usa",
                        animation_frame="timestamp", animation_group="location",height=550,width=900)
    #fig_us_map.write_image('res/fig_us_map.png')
    return fig_us_map

st.plotly_chart(us_ani())
##### us animation map ######

##### three nation's histogram cases #####
op_bar=['stack', 'group', 'overlay', 'relative']
sel_bar=st.selectbox('Choose Mode for Bar Plot', op_bar,0)
st.subheader('Comparing US, England and India(Daily Vaccinations per million)')
@st.cache
def three_hist(op_bar):
    e=df.dropna(subset=['total_vaccinations'],axis=0).query('country == "India" or country == "United States" or country == "England"').reset_index(drop=True)

    fig_3_nations = px.bar(e, x="date", y="daily_vaccinations_per_million",
                color="country",
                barmode = sel_bar,width=900, height=500)
    #fig_3_nations.write_image('res/fig_3_nations.png')
    return fig_3_nations
st.plotly_chart(three_hist(op_bar))#,use_container_width=True)
##### three nation's histogram cases #####

##### us statewise histogram ####
uss=pd.concat([uss.drop(uss[uss.code.isna()].index),uss.query('location=="New York State"')])
baruss=uss.groupby('location').agg({'date':'max','code':'last','total_vaccinations':'last',
                        'daily_vaccinations_per_million':'last',
                        'people_fully_vaccinated':'last'}).reset_index()
st.subheader('Top 20 US States(People fully Vaccinated)')                        
@st.cache
def top_20_states():
    fig_us_statewise = go.Figure(go.Bar(
                y=baruss.sort_values('people_fully_vaccinated',ascending=False).location[:20],x=baruss.sort_values('people_fully_vaccinated',ascending=False).people_fully_vaccinated[:20],orientation='h',text=baruss.sort_values('people_fully_vaccinated',ascending=False).people_fully_vaccinated[:20]))
    fig_us_statewise.update_layout(width=900, height=600,font=dict(
            family="Courier New, monospace",size=10))
    fig_us_statewise.update_traces(texttemplate='%{text:.3s}', textposition='outside')
    #fig_us_statewise.write_image('res/fig_us_20.png')
    return fig_us_statewise
st.plotly_chart(top_20_states())
##### us statewise histogram ####


#######complete##########skewness##
f=df.groupby('country').agg({'date':'max','total_vaccinations':'last',\
                        'daily_vaccinations_per_million':'last'}).reset_index().dropna()

percent_op=st.number_input('Enter the Percentage(to Handle the Right Skewness)',min_value=30,max_value=90,value=90)
percent_op/=100
left_column, right_column = st.columns(2)

@st.cache
def skew_table():
        fig = px.histogram(f.daily_vaccinations_per_million,marginal="rug")
        fig.add_trace(go.Scatter(x=[f.daily_vaccinations_per_million.max()*percent_op,f.daily_vaccinations_per_million.max()*percent_op], y=[0,50],name='Divider Line'))
        # fig.update_layout(labels=dict(x='No. of countries',y='Daily Vacc. per Million'))
        fig.update_layout(legend=dict(
    yanchor="top",
    y=1.1,
    xanchor="left",
    x=-0.01
))
        return fig   
with left_column: 
    st.markdown('Daily Vaccination per Million is **Highly Right Skewed**, So we take Percentage of Max value to cut out the Max value/s')
    with st.expander("See Definition"):
        st.header('Skewness')
        con="Skewness refers to a distortion or asymmetry that deviates from the symmetrical bell curve, or normal distribution, in a set of data" 
        st.write(con)               
        st.image('res/skewness.jpg',width=350)
    # st.image('rskew.png',width=350)
        st.latex(r'''Skewness=\frac{3(Mean-Mode)}{Standard Deviation}''')
st.subheader('Countries with Daily Vaccinations per million more than the percentage value')
st.table(f.dropna()[f.dropna().daily_vaccinations_per_million>f.dropna().daily_vaccinations_per_million.max()*percent_op].reset_index(drop=True))
with right_column:
    st.plotly_chart(skew_table())
f=f.dropna().drop(f.dropna()[f.dropna().daily_vaccinations_per_million>15000].index)
st.subheader(f'World Map of the Above Condition, Date {f.date.max()}')
@st.cache
def current_world():
    fig_current = px.choropleth(f, locations="country",
                        color="daily_vaccinations_per_million",
                        hover_data=["country",'total_vaccinations','date','daily_vaccinations_per_million'],
                        color_continuous_scale="Viridis",
                        locationmode = 'country names',
                        range_color=(f.daily_vaccinations_per_million.min(),f.daily_vaccinations_per_million.max()*percent_op)
                        ,height=500,width=900)
    #fig_current.write_image('res/fig_current.png')
    return fig_current
st.plotly_chart(current_world())
#######complete#########skewness##

def create_download_link(val, filename):
    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

if st.button('Download Report'):
    st.balloons()
    pdf = FPDF()
    pdf.add_page()
    pdf.image('res/pythongirl.jpg',0,0,210)
    pdf.add_font('AR DELANEY medium','B','res/ARDELANEY.TTF',uni=True)
    pdf.set_font('AR DELANEY medium', 'B', 70)
    pdf.text(50,290,'PDF Report')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.text(0,0,'Date : 02/04/2021')
    pdf.set_font('Arial', 'B', 16)
    pdf.image('res/fig_seven_nations.png',5,20,200,150)
    pdf.image('res/fig_current.png',3,170,210,150)
    pdf.add_page()
    pdf.image('res/fig_us_map.png',5,5,210,150)
    pdf.image('res/fig_3_nations.png',5,152,205,150)
    pdf.add_page()
    pdf.image('res/fig_seven_nations_line.png',5,3,190,160)
    pdf.add_font('AR CHRISTY medium','B','res/ARCHRISTY.TTF',uni=True)
    pdf.set_font('AR CHRISTY medium', 'B', 30)
    pdf.text(5,210,'Special Thanks to the open source Community ')
    pdf.text(5,240,'For Constant support and Always there for us')
    pdf.text(5,270,' ( And Also free ^_^) ')
    pdf.set_font('Times','',9)
    pdf.text(9,290,'Last updated Date is 02/04/2021 . Problem is being addressed . ')
    pdf.output('Vaccine Analysis.pdf', 'F')
    html=create_download_link(pdf.output(dest="S").encode("latin-1"), "vaccine")
    st.markdown(html, unsafe_allow_html=True)
    
