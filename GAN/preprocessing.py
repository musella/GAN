from sklearn.preprocessing import RobustScaler, QuantileTransformer
import pandas as pd
import numpy as np

default_tranformers = dict(minmax=RobustScaler(quantile_range=(10.,90.)),
                           gaus=QuantileTransformer(output_distribution="normal",n_quantiles=1000))

# ------------------------------------------------------------------------------------------------
def transform(data_x,data_c,mc_x,mc_c,transform='minmax',reshape=True,return_scalers=True):
    from sklearn.base import clone
    
    if type(transform) == str or type(transform) == unicode:
        transform = default_tranformers[transform]
    
    scaler_x = clone(transform)
    scaler_c = clone(transform)

    mc_x = scaler_x.fit_transform(mc_x)
    if not data_x is None:
        data_x = scaler_x.transform(data_x)

    if not mc_c is None:
        mc_c = scaler_c.fit_transform(mc_c)
        if not data_c is None:
            data_c = scaler_c.transform(data_c)

    if reshape:
        mc_x = mc_x.reshape(-1,1,mc_x.shape[-1])
        if not mc_c is None:
            mc_c = mc_c.reshape(-1,1,mc_c.shape[-1])
        if not data_x is None:
            data_x = data_x.reshape(-1,1,data_x.shape[-1])
        if not data_c is None:
            data_c = data_c.reshape(-1,1,data_c.shape[-1])
            
    if return_scalers:
        return data_x,data_c,mc_x,mc_c,scaler_x,scaler_c

    return data_x,data_c,mc_x,mc_c

# ------------------------------------------------------------------------------------------------
def reweight(mc,inputs,bins,weights,base=None,offset=True):

    def rewei(X):
        thebin = []
        for idim in range(len(weights.shape)):
            thebin.append(max(0,min(weights.shape[idim]-1,X[idim])))
        ## #xbin = max(0,min(weights.shape[0]-1,x[0]))
        ## #ybin = max(0,min(weights.shape[1]-1,x[1]))
        ## #return weights[xbin,ybin]
        return weights[tuple(thebin)]
    
    def discretize(df,col,bounds):
        ## print('offset',offset)
        ## print(bounds.shape)
        ## print(col)
        if offset:
            cmin = np.abs( df[col] ).min()
            vals = (np.abs(df[col])-cmin)*np.sign(df[col])
        else:
            vals = df[col]
        return pd.cut( vals,
                       bounds, labels=range(bounds.shape[0]-1) ).astype(np.int)

    # print(inputs)
    tmp = pd.DataFrame(  { inp[0] : discretize(mc,inp[0],inp[1]) for inp in zip(inputs,bins) } )
    ## mc['train_weight'] = tmp[inputs].apply( rewei, axis=1, raw=True)
    sample_weights = tmp[inputs].apply( rewei, axis=1, raw=True)
    if not base is None:
        ## mc['train_weight'] *= mc[base]
        sample_weights *= mc[base]
    
    return sample_weights



# ------------------------------------------------------------------------------------------------
def reweight_multidim(X,clf,epsilon = 1.e-3):
    probs = clf.predict_proba(X)
    return probs[:,1] / (probs[:,0] + epsilon )
    ## return np.apply_along_axis(lambda x: x[1]/(x[0]+epsilon), 1, clf.predict_proba(X))

