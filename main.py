import streamlit as st
import pandas as pd
import numpy as np
from pocketbase import PocketBase
from collections import defaultdict
import os

from sseclient import SSEClient

client = PocketBase(os.environ['PB_HOST'])
data = client.collection('users').auth_with_password(
    "web", os.environ["PB_PWD"]
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
    
    with st.expander('**Manual Control**'):
        st.subheader('	:globe_with_meridians: Box Door')
        box_door_on = st.toggle('CLOSE') 
        if box_door_on : st.write('OPEN')
        st.subheader('	:globe_with_meridians: Shaking Box')
        box_shaking_on = st.toggle('Off') 
        if box_shaking_on : st.write('on')

        client.collection('node_config').update(selected, {
            'box_door': box_door_on,
            'box_shaking': box_shaking_on
        })
    with st.expander('**Status Check**'):
        st.title('	:globe_with_meridians: Status Check')
        power = selected_node['power']
        lora = selected_node['lora_condition']
        camera = selected_node['camera_condition']
        current_detected = selected_node['currently_detected']
        status_display("Power", power)
        status_display("LoRA Condition", lora)
        status_display("Camera Condition", camera)
        status_display(f"Elephant {'' if current_detected else 'not'} Detected", not current_detected)


# tf
with right:
    fetch_detections()