# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
from matplotlib.pylab import plt
import featuretools as ft
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from Calculation import Calculate
import pickle
#import collections

def predict_type(data, threshold = 2, min_acc_value = 2):
    data.fillna(-1, inplace=True) 
    
    """ extract consective acceleraometer larger than n = threshold """
    mask = data['accelerometer'] .groupby((data['accelerometer']  != data['accelerometer'].shift()).cumsum()).transform('count').lt(threshold)
    mask &= data['accelerometer'].ge(min_acc_value)
    idx = mask[mask==True].index.tolist()
#    idx = data.index[data['accelerometer'] > 2].tolist()
        
    #group hits
    diff = [y - x for x, y in zip(*[iter(idx)] * 2)]
    avg = sum(diff) / len(diff)
    m = [[idx[0]]]
    for x in idx[1:]:
        if x - m[-1][0] < avg:
            m[-1].append(x)
        else:
            m.append([x])
     
    #extract max accleration and its index during the hits
    max_idx = []
    for item in m:
        max_idx.append(data.iloc[item].accelerometer.idxmax())
    
    sequences = pd.DataFrame()
    selected = pd.DataFrame()
    cnt = 0
    """ TYPE CLASSIFICATION"""
    for i in max_idx:
        cnt += 1
        values = data[['ax','ay','az','accelerometer','tilt1','tilt2','compass']].iloc[i-4:i+5].to_numpy().flatten()
        position_vector = Calculate(data[['ax','ay','az','accelerometer','tilt1','tilt2','compass']].iloc[i-4:i+5]).Position_Vector
        position = position_vector.flatten()
#        position = position[position!=0]  
        max_speed = Calculate(data[['ax','ay','az','accelerometer','tilt1','tilt2','compass']].iloc[i-4:i+5]).Max_Speed
        max_angle = Calculate(data[['ax','ay','az','accelerometer','tilt1','tilt2','compass']].iloc[i-4:i+5]).Max_Angle
        max_acc = data['accelerometer'].iloc[i]
        values = pd.Series(values)
        values = values.append(pd.Series(position), ignore_index=True)
        values['max_acc'] = max_acc
        sequences=sequences.append(values, ignore_index=True)
        
        new_col = pd.DataFrame({'ID':[cnt]*9, 'sx': np.append([0],position_vector[0,:]), 
                                'sy': np.append([0],position_vector[1,:]),
                                'sz': np.append([0],position_vector[2,:]),
                                'type':[-1]*9, 'type_str':['']*9, 'Max_Speed': [max_speed]*9, 'Max_Angle': [max_angle]*9})
        old_col = data[['tilt1','tilt2','compass','accelerometer','ax','ay','az']].iloc[i-4:i+5].reset_index(drop=True)
        df = pd.concat([old_col, new_col], axis=1)
        selected=selected.append(df, ignore_index=True)
    
    sequences["id"] = sequences.index + 1
    sequences.columns=sequences.columns.map(str)
    
    # creating and entity set 'es'
    es = ft.EntitySet(id = 'entity_type')
    # adding a dataframe 
    es.entity_from_dataframe(entity_id = 'predictors', dataframe = sequences, index = 'id')
    es.normalize_entity(base_entity_id='predictors', new_entity_id='max_acc', index='max_acc')
    
    feature_matrix, feature_names = ft.dfs(entityset=es, 
                                            target_entity = 'predictors', 
                                            max_depth = 2, 
                                            verbose = 1, 
                                            n_jobs = 1)

    feature_matrix = feature_matrix.dropna(axis=1,how='any')
    
    """ Read the model from disk """
    filename = 'finalized_model_type.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
#    saved_features = ft.load_features('feature_type.json')
#    es_test = ft.EntitySet(id = 'entity_type')
#    es_test.entity_from_dataframe(entity_id = 'predictors', dataframe = sequences, index = 'id')
#    es_test.normalize_entity(base_entity_id='predictors', new_entity_id='max_acc', index='max_acc')
#    feature_matrix = ft.calculate_feature_matrix(saved_features, es_test)
#    
#    feature_matrix.fillna(feature_matrix.mean(), inplace=True)
#    print(feature_matrix.describe)
    
    prediction = loaded_model.predict(feature_matrix)
    
    for i in range(int(len(selected)/9)):
        if prediction[i] == 1:
            pred_type = "Underhand";
        elif prediction[i] == 2:
            pred_type = "Overhand";
        elif prediction[i] == 3:
            pred_type = "Forehand";
        elif prediction[i] == 4:
            pred_type = "Backhand";
        else:
            pred_type = "Unable to predict type of swing."
        selected['type_str'].iloc[9*i:9*i+9] = pred_type
        selected['type'].iloc[9*i:9*i+9] = prediction[i]
       
#    ReturnType = collections.namedtuple('ReturnType', 'ID Type Max_Acc Max_Speed ')
#    return ReturnType(Type=pred_type, Position_Vector=position, Max_Acc=max_acc, Max_Speed=max_speed) 
    return selected

#cx = pd.read_excel('0119video.xlsx', sheet_name = 'CX')
#candidates=predict_type(cx)
from scipy.ndimage.filters import gaussian_filter1d
from matplotlib import gridspec
from scipy.interpolate import make_interp_spline, BSpline

def plot_four(plot_data):
    
    fig = plt.figure(figsize=(20, 10))
    
#    gs = gridspec.GridSpec(1, 2, height_ratios=[1, 2]) 
    
    ax = fig.add_subplot(223, projection='3d')
    ax.scatter(plot_data['sx'],  plot_data['sy'], plot_data['sz'])
    ax.plot(plot_data['sx'],  plot_data['sy'], plot_data['sz'], color='b')
    ax.view_init(azim=0, elev=90) #xy plane
    plt.xticks(fontsize=10)
    ax.set_title('Displacement Projection in xy Plane',size=20)

    ax2 = fig.add_subplot(224, projection='3d')
    ax2.scatter(plot_data['sx'],  plot_data['sy'], plot_data['sz'])
    ax2.plot(plot_data['sx'],  plot_data['sy'], plot_data['sz'], color='b')
    ax2.view_init(azim=0, elev=45) 
    ax2.set_title('Displacement',size=20)

    ax3 = fig.add_subplot(221)
    # 50 represents number of points to make between T.min and T.max
    xnew = np.linspace(0,8,50) 
    spl = make_interp_spline(pd.Series(range(9)), plot_data['tilt1'], k=3)  # type: BSpline
    x = spl(xnew)
    spl = make_interp_spline(pd.Series(range(9)), plot_data['tilt2'], k=3)  # type: BSpline
    y = spl(xnew)
    spl = make_interp_spline(pd.Series(range(9)), plot_data['compass'], k=3)  # type: BSpline
    z = spl(xnew)
    ax3.plot(x,"b-",label='tilt1')
    ax3.plot(y,"r-",label='tilt2')
    ax3.plot(z,"g-",label='compass')
    ax3.legend(loc="lower left",prop={'size': 20})
    ax3.set_title('Orientation Plot (degree)',size=20)
    ax3.tick_params(labelsize=20)
    
    ax4 = fig.add_subplot(222)
#    x = gaussian_filter1d(plot_data['ax'], sigma=1)    
#    y = gaussian_filter1d(plot_data['ay'], sigma=1)   
#    z = gaussian_filter1d(plot_data['az'], sigma=1)   
#    mag = gaussian_filter1d(plot_data['accelerometer'], sigma=1)   
    spl = make_interp_spline(pd.Series(range(9)), plot_data['ax'], k=3)  # type: BSpline
    x = spl(xnew)
    spl = make_interp_spline(pd.Series(range(9)), plot_data['ay'], k=3)  # type: BSpline
    y = spl(xnew)
    spl = make_interp_spline(pd.Series(range(9)), plot_data['az'], k=3)  # type: BSpline
    z = spl(xnew)
    spl = make_interp_spline(pd.Series(range(9)), plot_data['accelerometer'], k=3)  # type: BSpline
    mag = spl(xnew)
    ax4.plot(x/1000,"c--",label='ax')
    ax4.plot(y/1000,"g--",label='ay')
    ax4.plot(z/1000,"b--",label='az')
    ax4.plot(mag,"r-",label='Acc')

    ax4.legend(loc="lower left",prop={'size': 20})
    ax4.set_title('Acceleration Plot (g)',size=20)
    ax4.tick_params(labelsize=20)
    
    plt.tight_layout()
    plt.show()
    fig.savefig('FourInOne.png')
    
#plot_four(candidates.iloc[0:9])
#predict_type(cx)
