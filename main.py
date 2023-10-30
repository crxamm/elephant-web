import streamlit as st
import pandas as pd
import numpy as np
from pocketbase import PocketBase
from collections import defaultdict
import os

from sseclient import SSEClient

client = PocketBase('https://elephant-detection.pockethost.io')
data = client.collection('users').auth_with_password(
    "web", "mgskWGePQM54kYG"
)

node_config = client.collection('node_config').get_full_list()
nodes_lst = [node.__dict__ for node in node_config]
nodes_id = [node['id'] for node in nodes_lst]
nodes = pd.DataFrame.from_dict(nodes_lst)

selected_node = nodes_lst[0]

result = client.collection('detections').get_full_list()
st.set_page_config(page_title='Prevention System', page_icon='elephant:',layout='wide')
st.title(':elephant: Wild Elephants Prevention System Information')
fl = st.subheader(':dizzy: Show Data')
# st.snow()

def fetch_detections():
    detections = []
    for res in result:
        res.__dict__.pop('expand')
        res.__dict__.pop('collection_id')
        res.__dict__.pop('collection_name')
        res.__dict__.pop('updated')
        detections.append(res.__dict__)

    data = pd.DataFrame.from_dict(detections)
    if len(detections) != 0:
        data['created'] = data['created'].dt.tz_localize('UTC').dt.tz_convert('Asia/Bangkok')
        data['date'] = data['created'].dt.date
        data['time'] = data['created'].dt.time


        data = data.drop('created', axis='columns')
        data['time'] = data['time'].astype(str)
        data = data[data['node_id'] == selected]
    st.table(data)


def status_display(name, status):
    if(status):
        st.success(name, icon="✅")
    else:
        st.error(name, icon="🚨")
    

selected = st.selectbox("**Choose node**", nodes_id,
                 format_func=lambda option: option.split('_')[0])
selected_node = nodes.loc[nodes['id'] == selected].iloc[0] # make the option looks friendlier

left, right = st.columns(2)
with left:
    
    st.title('	:loudspeaker: Status Check')
    current_detected = selected_node['currently_detected']
    status_display(f"Elephant {'' if current_detected else 'not'} Detected", not current_detected)
    power = selected_node['power']
    lora = selected_node['lora_condition']
    camera = selected_node['camera_condition']
    status_display("Power", power)
    status_display("LoRA Condition", lora)
    status_display("Camera Condition", camera)
    wifi = nodes.loc[nodes['id'] == 'master12xojekmv'].iloc[0]['wifi']
    status_display("Wifi", wifi)


# tf
with right:
        st.title(':wrench: Manual Control')
        st.subheader(' Box Door')
        box_door_on = st.toggle('door close') 
        if box_door_on : st.write('door open')

        st.subheader('Vibrate Box')
        box_shaking_on = st.toggle('not shaking') 
        if box_shaking_on : st.write('shaking')

        client.collection('node_config').update(selected, {
            'box_door': box_door_on,
            'box_shaking': box_shaking_on
        })
        fetch_detections()