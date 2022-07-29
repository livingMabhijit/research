# from asyncio.windows_events import NULL
from curses import keyname
import pandas as pd
import numpy as np
import streamlit as st
import pickle
from sklearn import preprocessing
import matplotlib.pyplot as plt
import streamlit as st
from bokeh.plotting import figure
from bokeh.layouts import gridplot
import streamlit.components.v1 as components
import chnage

with open('/Users/apple/Documents/work_DFA/Labelizer/current_index.txt') as f:
    lines = f.readlines()
    
    line = lines[-1]
    print(lines)
    f.close()

print(st.session_state)

#------------------------ Home Page setup -------------------------------
st.set_page_config(
     page_title="DFA Labelizer",
     layout="wide"   
 )

st.sidebar.header('Page Navigation')
navigation_tab = st.sidebar.selectbox('Choose Page', ('Labelizer','Label verify'))
#------------------ Page set up ends ----------------------------------
if navigation_tab == 'Labelizer':
    

    st.write(""" ## DFA Labelizer """)

    ## Data
    x  = np.load("/Users/apple/Documents/work_DFA/Labelizer/saved_RMS_v16_with_bias_2k.npy",allow_pickle=True)
    x_raw = np.load("/Users/apple/Documents/work_DFA/Labelizer/saved_RMS_v16_raw_2k.npy",allow_pickle=True)
    # y = np.load("/Users/apple/Documents/work_DFA/RMS verification app/saved_RMS_label_v14_with_bias.npy",allow_pickle=True)
    main_file = pd.read_csv('/Users/apple/Documents/work_DFA/Labelizer/main_file_error_v1_2k.csv',sep = '\t') # curated dataframe for only actual , pred class as file name
    # labels_unique = main_file['label'].unique()

    #key value holder
    vals={10110:'Capacitor on',10120: 'Capacitor off',12110: 'Motor start',13170: 'Inrush',15110: 'OC normal'} 
    ######################################################################### NEW CODE FOR NEXT ISSUE #################
    #main function for plotting RMS and button config
    with st.container():

        def first_page(idx):
            # main_file = pd.read_csv('/Users/apple/Documents/work_DFA/RMS verification app/main_file_error.csv',sep = '\t') # curated dataframe for only actual , pred class as file name
            # idx = idx
            
            classes = ["10110: Capacitor on","10120: Capacitor off","12110: Motor start","13170: Inrush","15110: OC normal"]
            for i in classes:
                if i[0:5]==str(main_file['label'][idx]): #comaring first 5 char e.g '15110'  with the string value of class list
                    cl_index = i # this will later used for what will be the default value for radio button 
                # else:
                #     continue

            
            # actual classes fetched from DB
            # actual_classification_code = st.text_input('Actual classification code', vals[main_file['label'][idx]] ,  key = idx,disabled=True)
            col_1, col_2, = st.columns(2)

            with col_1:
                st.write('Ground Truth')
                st.header( vals[main_file['label'][idx]] )
            with col_2:
                st.write('Predicted class')
                st.header( vals[main_file['pred'][idx]] )

            
            # st.header( vals[main_file['label'][idx]] )
            # value of index parameter in radio button for default value
            pred_index = classes.index(cl_index)
            pred_classification_code = st.radio("Change classification code to",classes ,index = pred_index ,key = 'my_radio'+str(st.session_state.count))#,on_change=new_val)
            
            # if value changes radio button to capture the new value
            if st.session_state['my_radio'+str(st.session_state.count)] in classes:
                pred_classification_code = (st.session_state['my_radio'+str(st.session_state.count)])[0:5]
                chnage.change_df(x = pred_classification_code,idx = st.session_state.count )
            
            #### Plot starts
            st.write(str(idx)+' - PQD Filename '+str(main_file['file_name'][idx]))
            # st.button('View file')
            link = '[View file] https://dfa.plus/grid/?plot_files='+ str(main_file['file_name'][idx])
            st.markdown(link, unsafe_allow_html=True)

            
            col_orig, col_scaled, = st.columns(2)
            with col_orig:
                RAW_RMS = st.button('Original RMS')
            with col_scaled:
                SCALED_RMS = st.button('Scaled RMS')
            
            
            ##plot Normalized
            print(idx)
            x1 = [i for i in range(60,180)]
            
            p1 = figure(plot_width=600,plot_height=200,)
            p2 = figure(plot_width=600,plot_height=200)
            p3 = figure(plot_width=600,plot_height=200)
            p4 = figure(plot_width=600,plot_height=200)
            p5 = figure(plot_width=600,plot_height=200)
            p6 = figure(plot_width=600,plot_height=200)
            
            #VA_VB_VC
            y1 = x_raw[idx,:,0]
            y2 = x_raw[idx,:,1]
            y3 = x_raw[idx,:,2]  
            if SCALED_RMS is True :
                y1 = x[idx,:,1]
                y2 = x[idx,:,2]
                y3 = x[idx,:,3] 
            p1.line(x1,y1,color = 'red')
            p1.line(x1,y2,color = 'green')
            p1.line(x1,y3,color = 'blue')

            #IA_IB_IC
            y5 = x_raw[idx,:,3]
            y6 = x_raw[idx,:,4]
            y7 = x_raw[idx,:,5]
            if SCALED_RMS is True:
                y5 = x[idx,:,5]
                y6 = x[idx,:,6]
                y7 = x[idx,:,7]
            p2.line(x1,y5,color = 'red')
            p2.line(x1,y6,color = 'green')
            p2.line(x1,y7,color = 'blue')

            #IEVEN
            y17 = x_raw[idx,:,12]
            y18 = x_raw[idx,:,13]
            y19 = x_raw[idx,:,14]
            if SCALED_RMS is True:
                y17 = x[idx,:,17]
                y18 = x[idx,:,18]
                y19 = x[idx,:,19]
            
            p3.line(x1,y17,color = 'red')
            p3.line(x1,y18,color = 'green')
            p3.line(x1,y19,color = 'blue')
            
            #IODD
            y21 = x_raw[idx,:,15]
            y22 = x_raw[idx,:,16]
            y23 = x_raw[idx,:,17]
            if SCALED_RMS is True:
                y21 = x[idx,:,21]
                y22 = x[idx,:,22]
                y23 = x[idx,:,23]
            
            p4.line(x1,y21,color = 'red')
            p4.line(x1,y22,color = 'green')
            p4.line(x1,y23,color = 'blue')

            #PA_PB_PC
            y25 = x_raw[idx,:,18]
            y26 = x_raw[idx,:,19]
            y27 = x_raw[idx,:,20]
            if SCALED_RMS is True:
                y25 = x[idx,:,25]
                y26 = x[idx,:,26]
                y27 = x[idx,:,27]
            p5.line(x1,y25,color = 'red')
            p5.line(x1,y26,color = 'green')
            p5.line(x1,y27,color = 'blue')
            
            #QA_QB_QC
            y29 = x_raw[idx,:,21]
            y30 = x_raw[idx,:,22]
            y31 = x_raw[idx,:,23]
            if SCALED_RMS is True:
                y29 = x[idx,:,29]
                y30 = x[idx,:,30]
                y31 = x[idx,:,31]
            p6.line(x1,y29,color = 'red')
            p6.line(x1,y30,color = 'green')
            p6.line(x1,y31,color = 'blue')

            col1, col2,col3  = st.columns(3)
            col4,col5,col6 = st.columns(3)

            with col1:
                st.write('Voltage')
                st.bokeh_chart(p1, use_container_width=False,)
        
            with col2:
                st.write('Real Power')
                st.bokeh_chart(p5, use_container_width=False)
            
            with col3:
                st.write('Current Even')
                st.bokeh_chart(p3, use_container_width=False)
            
            with col4:
                st.write('Current')
                st.bokeh_chart(p2, use_container_width=False)
            
            with col5:
                st.write('Reactive Power')
                st.bokeh_chart(p6, use_container_width=False)
                
            with col6:
                st.write('Current Odd')
                st.bokeh_chart(p4, use_container_width=False)

            return pred_classification_code,idx

    def radio_change():
            pred_classification_code_next = (st.session_state['my_radio'+str(st.session_state.count)])[0:5]
            chnage.change_df(x = pred_classification_code_next,idx = st.session_state.count )
    def main(idx):
        # main_file = pd.read_csv('/Users/apple/Documents/work_DFA/RMS verification app/main_file_error.csv',sep = '\t') # curated dataframe for only actual , pred class as file name
        # idx = idx
        classes = ["10110: Capacitor on","10120: Capacitor off","12110: Motor start","13170: Inrush","15110: OC normal"]
        for i in classes:
            if i[0:5]==str(main_file['label'][idx]): #comaring first 5 char e.g '15110'  with the string value of class list
                cl_index = i # this will later used for what will be the default value for radio button 
            # else:
            #     continue
        # actual classes fetched from DB
        # actual_classification_code = st.text_input('Actual classification code', vals[main_file['label'][idx]] ,  key = idx,disabled=True)
        
        col_1, col_2, = st.columns(2)

        with col_1:
            st.write('Ground Truth')
            st.header( vals[main_file['label'][idx]] )
        with col_2:
            st.write('Predicted class')
            st.header( vals[main_file['pred'][idx]] )
        
        # st.header( vals[main_file['label'][idx]] )
        # value of index parameter in radio button for default value
        pred_index = classes.index(cl_index)
        pred_classification_code_next = st.radio("Change classification code to",classes ,index = pred_index ,key = 'my_radio'+str(st.session_state.count),on_change=radio_change)
        
        # if value changes radio button to capture the new value
        # if st.session_state['my_radio'+str(st.session_state.count)] in classes:
        # # def radio_change():
        #     pred_classification_code_next = (st.session_state['my_radio'+str(st.session_state.count)])[0:5]
        #     chnage.change_df(x = pred_classification_code_next,idx = st.session_state.count )
        
        #### Plot starts
        st.write(str(idx)+' - PQD Filename '+str(main_file['file_name'][idx]))
        link = '[View file] https://dfa.plus/grid/?plot_files='+ str(main_file['file_name'][idx])
        st.markdown(link, unsafe_allow_html=True)

        
        col_orig, col_scaled, = st.columns(2)
        with col_orig:
            RAW_RMS = st.button('Original RMS')
        with col_scaled:
            SCALED_RMS = st.button('Scaled RMS')
        
        
        ##plot Normalized
        print(idx)
        x1 = [i for i in range(60,180)]
        
        p1 = figure(plot_width=600,plot_height=200,)
        p2 = figure(plot_width=600,plot_height=200)
        p3 = figure(plot_width=600,plot_height=200)
        p4 = figure(plot_width=600,plot_height=200)
        p5 = figure(plot_width=600,plot_height=200)
        p6 = figure(plot_width=600,plot_height=200)
        
        #VA_VB_VC
        y1 = x_raw[idx,:,0]
        y2 = x_raw[idx,:,1]
        y3 = x_raw[idx,:,2]  
        if SCALED_RMS is True :
            y1 = x[idx,:,1]
            y2 = x[idx,:,2]
            y3 = x[idx,:,3] 
        p1.line(x1,y1,color = 'red')
        p1.line(x1,y2,color = 'green')
        p1.line(x1,y3,color = 'blue')

        #IA_IB_IC
        y5 = x_raw[idx,:,3]
        y6 = x_raw[idx,:,4]
        y7 = x_raw[idx,:,5]
        if SCALED_RMS is True:
            y5 = x[idx,:,5]
            y6 = x[idx,:,6]
            y7 = x[idx,:,7]
        p2.line(x1,y5,color = 'red')
        p2.line(x1,y6,color = 'green')
        p2.line(x1,y7,color = 'blue')

        #IEVEN
        y17 = x_raw[idx,:,12]
        y18 = x_raw[idx,:,13]
        y19 = x_raw[idx,:,14]
        if SCALED_RMS is True:
            y17 = x[idx,:,17]
            y18 = x[idx,:,18]
            y19 = x[idx,:,19]
        p3.line(x1,y17,color = 'red')
        p3.line(x1,y18,color = 'green')
        p3.line(x1,y19,color = 'blue')
        
        #IODD
        y21 = x_raw[idx,:,15]
        y22 = x_raw[idx,:,16]
        y23 = x_raw[idx,:,17]
        if SCALED_RMS is True:
            y21 = x[idx,:,21]
            y22 = x[idx,:,22]
            y23 = x[idx,:,23]
        p4.line(x1,y21,color = 'red')
        p4.line(x1,y22,color = 'green')
        p4.line(x1,y23,color = 'blue')

        #PA_PB_PC
        y25 = x_raw[idx,:,18]
        y26 = x_raw[idx,:,19]
        y27 = x_raw[idx,:,20]
        if SCALED_RMS is True:
            y25 = x[idx,:,25]
            y26 = x[idx,:,26]
            y27 = x[idx,:,27]
        p5.line(x1,y25,color = 'red')
        p5.line(x1,y26,color = 'green')
        p5.line(x1,y27,color = 'blue')
        
        #QA_QB_QC
        y29 = x_raw[idx,:,21]
        y30 = x_raw[idx,:,22]
        y31 = x_raw[idx,:,23]
        if SCALED_RMS is True:
            y29 = x[idx,:,29]
            y30 = x[idx,:,30]
            y31 = x[idx,:,31]
        p6.line(x1,y29,color = 'red')
        p6.line(x1,y30,color = 'green')
        p6.line(x1,y31,color = 'blue')

            
        col1, col2,col3  = st.columns(3)
        col4,col5,col6 = st.columns(3)

        with col1:
            st.write('Voltage')
            st.bokeh_chart(p1, use_container_width=False,)
        
        with col2:
            st.write('Real Power')
            st.bokeh_chart(p5, use_container_width=False)
        
        with col3:
            st.write('Current Even')
            st.bokeh_chart(p3, use_container_width=False)
        
        with col4:
            st.write('Current')
            st.bokeh_chart(p2, use_container_width=False)
        
        with col5:
            st.write('Reactive Power')
            st.bokeh_chart(p6, use_container_width=False)
            
        with col6:
            st.write('Current Odd')
            st.bokeh_chart(p4, use_container_width=False)


        return pred_classification_code_next,idx

    def radio_change_prev():
        pred_classification_code_prev = (st.session_state['my_radio'+str(st.session_state.count)])[0:5]
        chnage.change_df(x = pred_classification_code_prev,idx = st.session_state.count )

    def main_prev(idx):
        
        # main_file = pd.read_csv('/Users/apple/Documents/work_DFA/Labelizer/main_file_error.csv',sep = '\t')
        # idx = idx
        classes = ["10110: Capacitor on","10120: Capacitor off","12110: Motor start","13170: Inrush","15110: OC normal"]
        for i in classes:
            if i[0:5]==str(main_file['label'][idx]): #comaring first 5 char e.g '15110'  with the string value of class list
                cl_index = i # this will later used for what will be the default value for radio button 
        # actual classes fetched from DB
        # actual_classification_code_prev = st.text_input('Actual classification code', vals[main_file['label'][idx]] ,  key = idx-1,disabled=True)
        
        col_1, col_2, = st.columns(2)

        with col_1:
            st.write('Ground Truth')
            st.header( vals[main_file['label'][idx]] )
        with col_2:
            st.write('Predicted class')
            st.header( vals[main_file['pred'][idx]] )
        
        # st.header( vals[main_file['label'][idx]] )
        # value of index parameter in radio button for default value
        pred_index = classes.index(cl_index)
        pred_classification_code_prev = st.radio("Change classification code to",classes ,index = pred_index ,key = 'my_radio'+str(st.session_state.count),on_change=radio_change_prev)
        
        # # if value changes radio button to capture the new value
        # if st.session_state['my_radio'+str(st.session_state.count)] in classes:
        #     pred_classification_code_prev = (st.session_state['my_radio'+str(st.session_state.count)])[0:5]
        #     chnage.change_df(x = pred_classification_code_prev,idx = st.session_state.count )
        
        #### Plot starts
        st.write(str(idx)+' - PQD Filename '+str(main_file['file_name'][idx]))
        link = '[View file] https://dfa.plus/grid/?plot_files='+ str(main_file['file_name'][idx])
        st.markdown(link, unsafe_allow_html=True)

        col_orig, col_scaled, = st.columns(2)
        with col_orig:
            RAW_RMS = st.button('Original RMS')
        with col_scaled:
            SCALED_RMS = st.button('Scaled RMS')
        
        
        ##plot Normalized
        print(idx)
        x1 = [i for i in range(60,180)]
        
        p1 = figure(plot_width=600,plot_height=200)
        p2 = figure(plot_width=600,plot_height=200)
        p3 = figure(plot_width=600,plot_height=200)
        p4 = figure(plot_width=600,plot_height=200)
        p5 = figure(plot_width=600,plot_height=200)
        p6 = figure(plot_width=600,plot_height=200)
        
        #VA_VB_VC
        y1 = x_raw[idx,:,0]
        y2 = x_raw[idx,:,1]
        y3 = x_raw[idx,:,2]  
        if SCALED_RMS is True :
            y1 = x[idx,:,1]
            y2 = x[idx,:,2]
            y3 = x[idx,:,3] 
        p1.line(x1,y1,color = 'red')
        p1.line(x1,y2,color = 'green')
        p1.line(x1,y3,color = 'blue')

        #IA_IB_IC
        y5 = x_raw[idx,:,3]
        y6 = x_raw[idx,:,4]
        y7 = x_raw[idx,:,5]
        if SCALED_RMS is True:
            y5 = x[idx,:,5]
            y6 = x[idx,:,6]
            y7 = x[idx,:,7]
        p2.line(x1,y5,color = 'red')
        p2.line(x1,y6,color = 'green')
        p2.line(x1,y7,color = 'blue')

        #IEVEN
        y17 = x_raw[idx,:,12]
        y18 = x_raw[idx,:,13]
        y19 = x_raw[idx,:,14]
        if SCALED_RMS is True:
            y17 = x[idx,:,17]
            y18 = x[idx,:,18]
            y19 = x[idx,:,19]
        p3.line(x1,y17,color = 'red')
        p3.line(x1,y18,color = 'green')
        p3.line(x1,y19,color = 'blue')
        
        #IODD
        y21 = x_raw[idx,:,15]
        y22 = x_raw[idx,:,16]
        y23 = x_raw[idx,:,17]
        if SCALED_RMS is True:
            y21 = x[idx,:,21]
            y22 = x[idx,:,22]
            y23 = x[idx,:,23]
        p4.line(x1,y21,color = 'red')
        p4.line(x1,y22,color = 'green')
        p4.line(x1,y23,color = 'blue')

        #PA_PB_PC
        y25 = x_raw[idx,:,18]
        y26 = x_raw[idx,:,19]
        y27 = x_raw[idx,:,20]
        if SCALED_RMS is True:
            y25 = x[idx,:,25]
            y26 = x[idx,:,26]
            y27 = x[idx,:,27]
        p5.line(x1,y25,color = 'red')
        p5.line(x1,y26,color = 'green')
        p5.line(x1,y27,color = 'blue')
        
        #QA_QB_QC
        y29 = x_raw[idx,:,21]
        y30 = x_raw[idx,:,22]
        y31 = x_raw[idx,:,23]
        if SCALED_RMS is True:
            y29 = x[idx,:,29]
            y30 = x[idx,:,30]
            y31 = x[idx,:,31]
        p6.line(x1,y29,color = 'red')
        p6.line(x1,y30,color = 'green')
        p6.line(x1,y31,color = 'blue')

        col1, col2,col3  = st.columns(3)
        col4,col5,col6 = st.columns(3)

        with col1:
            st.write('Voltage')
            st.bokeh_chart(p1, use_container_width=False,)
        
        with col2:
            st.write('Real Power')
            st.bokeh_chart(p5, use_container_width=False)
        
        with col3:
            st.write('Current Even')
            st.bokeh_chart(p3, use_container_width=False)
        
        with col4:
            st.write('Current')
            st.bokeh_chart(p2, use_container_width=False)
        
        with col5:
            st.write('Reactive Power')
            st.bokeh_chart(p6, use_container_width=False)
            
        with col6:
            st.write('Current Odd')
            st.bokeh_chart(p4, use_container_width=False)

        return pred_classification_code_prev,idx


    # Keyboard part
    # def next_callback():
    #     st.write('Next was clicked')
    # def prev_callback():
    #     st.write('Prev was clicked')

    st.session_state.count = int(line)

    if 'count' not in st.session_state:
        st.session_state.count = 2
        # executed_lines = []

    left_col, right_col= st.columns(2)

    with right_col:
        if st.session_state.count != len(x):
            next_btn = st.button('Next')
        else:
            next_btn = st.button('Next',disabled=True)
    with left_col:
        if st.session_state.count != 0:
            prev_button = st.button('Prev')
        else:
            prev_button = st.button('Prev', disabled=True)

    ## session_state monitor for next & prev selection
    # if next_btn:
    #     st.session_state.count += 1

        
    # if prev_button:
    #     st.session_state.count -= 1
    #     actual_classification_code_prev, pred_classification_code_prev,idx = main_prev(idx = st.session_state.count)
        

    ### Next and previous button with final render
    if next_btn is False and prev_button is False:
        pred_classification_code,idx =  first_page(idx = st.session_state.count)
        # print(str(pred_classification_code))
        # print('s_count in if is '+str(idx) )
    elif prev_button is True and next_btn is False:
        st.session_state.count -= 1
        pred_classification_code_prev,idx = main_prev(idx = st.session_state.count)

    elif next_btn is True and prev_button is False:
        st.session_state.count += 1
        pred_classification_code_next,idx =  main(idx = st.session_state.count)
        # print(str(pred_classification_code))
        # print('s_count else is '+str(idx) )



    # executed_lines.append(idx)
    with open('/Users/apple/Documents/work_DFA/Labelizer/current_index.txt', 'w') as f:
        f.write(str(st.session_state.count))
        f.close()


    components.html(
        """
    <script>
    const doc = window.parent.document;
    buttons = Array.from(doc.querySelectorAll('button[kind=primary]'));
    const next_button = buttons.find(el => el.innerText === 'Next');
    const prev_button = buttons.find(el => el.innerText === 'Prev');
    const raw_RMS = buttons.find(el => el.innerText === 'RMS');

    radio_buttons = Array.from(doc.querySelectorAll('label[data-baseweb=radio]'));
    const correction_1 = radio_buttons.find(el => el.innerText === '10110: Capacitor on');
    const correction_2 = radio_buttons.find(el => el.innerText === '10120: Capacitor off');
    const correction_3 = radio_buttons.find(el => el.innerText === '12110: Motor start');
    const correction_4 = radio_buttons.find(el => el.innerText === '13170: Inrush');
    const correction_5 = radio_buttons.find(el => el.innerText === '15110: OC normal');


    doc.addEventListener('keydown', function(e) {
        switch (e.keyCode) {
            case 13: // (13 = enter)
                next_button.click();
                break;
            case 8: // (8 = back space)
                prev_button.click();
                break;

            case 82: // (82 = r)
                raw_RMS.click();
                break;

            case 49: // (49 = num 1)
                correction_1.click();
                break;
            case 50: // (50 = num 2)
                correction_2.click();
                break;
            case 51: // (51 = num 3)
                correction_3.click();
                break;
            case 52: // (52 = num 4)
                correction_4.click();
                break;
            case 53: // (53 = num 5)
                correction_5.click();
                break;
        }
    });
    </script>
    """,
        height=0,
        width=0,
    )
elif navigation_tab == 'Label verify':
    st.header('Label verify page')
    
    main_file_verify = pd.read_csv('/Users/apple/Documents/work_DFA/Labelizer/main_file_error_v1_2k.csv',sep = '\t')
    x_arr  = np.load("/Users/apple/Documents/work_DFA/Labelizer/saved_RMS_v16_with_bias_2k.npy",allow_pickle=True)
    
    
    vals={'Capacitor on':10110,'Capacitor off':10120,'Motor start':12110,'Inrush':13170,'OC normal':15110}
    option = st.selectbox(
     'Select the error code',
     ('Capacitor on',
      'Capacitor off',
       'Motor start',
       'Inrush',
       'OC normal'
       ))
    selection = vals[option]

    print('sel '+ str(selection))
    
    selected_df = main_file_verify[main_file_verify.label ==selection]
    
    
    col_1, col_2  = st.columns(2)
    
    with col_1:
        # src1 = 
        for idx in selected_df.index[0:51] :
            x1 = [i for i in range(60,180)]
            p1 = figure(plot_width=300,plot_height=150)
            p2 = figure(plot_width=300,plot_height=150)

            #VA_VB_VC
            y1 = x_arr[idx,:,1]
            y2 = x_arr[idx,:,2]
            y3 = x_arr[idx,:,3]  
            
            p1.line(x1,y1,color = 'red')
            p1.line(x1,y2,color = 'green')
            p1.line(x1,y3,color = 'blue')

            #IA_IB_IC
            y5 = x_arr[idx,:,5]
            y6 = x_arr[idx,:,6]
            y7 = x_arr[idx,:,7]

            p2.line(x1,y5,color = 'red')
            p2.line(x1,y6,color = 'green')
            p2.line(x1,y7,color = 'blue')
            # gr1 = gridplot([[p1,p2]])
            # st.bokeh_chart(p1, use_container_width=False)

            st.write(str(idx)+' - PQD Filename '+str(selected_df['file_name'][idx]))
            st.write('Voltage & Current')
            # st.bokeh_chart(gr1, use_container_width=False)
            st.bokeh_chart(p1, use_container_width=False)
            st.bokeh_chart(p2, use_container_width=False)

    with col_2:
        # src2 = 
        for idx in selected_df.index[51:100]:
            x1 = [i for i in range(60,180)]
            p1 = figure(plot_width=300,plot_height=150)
            p2 = figure(plot_width=300,plot_height=150)

            #VA_VB_VC
            y1 = x_arr[idx,:,1]
            y2 = x_arr[idx,:,2]
            y3 = x_arr[idx,:,3]  
            
            p1.line(x1,y1,color = 'red')
            p1.line(x1,y2,color = 'green')
            p1.line(x1,y3,color = 'blue')

            #IA_IB_IC
            y5 = x_arr[idx,:,5]
            y6 = x_arr[idx,:,6]
            y7 = x_arr[idx,:,7]

            p2.line(x1,y5,color = 'red')
            p2.line(x1,y6,color = 'green')
            p2.line(x1,y7,color = 'blue')
            gr2 = gridplot([[p1,p2]])

            st.write(str(idx)+' - PQD Filename '+str(selected_df['file_name'][idx]))
            st.write('Voltage & Current')
            # st.bokeh_chart(gr2, use_container_width=False)
            st.bokeh_chart(p1, use_container_width=False)
            st.bokeh_chart(p2, use_container_width=False)




    # print(selected_df.index)
    # x1 = [i for i in range(60,180)]
    # p1 = figure(plot_width=300,plot_height=150)
    # p2 = figure(plot_width=300,plot_height=150)
    # # col_1, col_2  = st.columns(2)
    
    # # with col_1:
    # for idx in selected_df.index[0:100]:
        

    #     #VA_VB_VC
    #     y1 = x[idx,:,1]
    #     y2 = x[idx,:,2]
    #     y3 = x[idx,:,3]  
        
    #     p1.line(x1,y1,color = 'red')
    #     p1.line(x1,y2,color = 'green')
    #     p1.line(x1,y3,color = 'blue')

    #     #IA_IB_IC
    #     y5 = x[idx,:,5]
    #     y6 = x[idx,:,6]
    #     y7 = x[idx,:,7]

    #     p2.line(x1,y5,color = 'red')
    #     p2.line(x1,y6,color = 'green')
    #     p2.line(x1,y7,color = 'blue')
    #     gr = gridplot([[p1,p2]])

    #     col1, col2  = st.columns(2)
    #     with col1:
    #         st.write(str(idx)+' - PQD Filename '+str(selected_df['file_name'][idx]))
    #         st.write('Voltage & Current')
    #         st.bokeh_chart(gr, use_container_width=True)
    #         # st.write('Current')
    #         # st.bokeh_chart(p2, use_container_width=False)
            
    #     with col2:
    #         st.write(str(idx)+' - PQD Filename '+str(selected_df['file_name'][idx]))
    #         st.write('Voltage & Current')
    #         st.bokeh_chart(gr, use_container_width=True)
        


    
