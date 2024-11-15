#Hydrological_Model_with_Snow_and_Soil_Reservoirs
import numpy as np

# model 1
def model_01(Sini,Pvec,EpotVec,tempVec,theta,delT):
    # Initialize variables
    nT=len(Pvec)
    Qvec=np.empty(nT)
    Qvec[:]=np.nan
    EactVec=np.empty(nT)
    EactVec[:]=np.nan
    # parameters
    Kmlt_WR=theta[0]
    tempThr_WR=0.0
    Smax_UR=theta[1]
    K_UR=theta[2]
    theta_WR=[Kmlt_WR,tempThr_WR]
    theta_UR=[Smax_UR,K_UR]
    # states
    Svec_WR=np.empty(nT)
    Svec_WR[:]=np.nan
    Svec_UR=np.empty(nT)
    Svec_UR[:]=np.nan
    Scurrent_WR=Sini[0]
    Scurrent_UR=Sini[1]*Smax_UR #Sini[1] is the dimensionless propotion which shows how full the unsaturated zone is.
    # loop trhough time series
    for iT in range(nT):
        P=Pvec[iT]
        Epot=EpotVec[iT]
        Temp=tempVec[iT]
        Sini_WR=Scurrent_WR
        Sini_UR=Scurrent_UR
        Scurrent_WR,Prain,Qmelt=WR_ResExp(Sini_WR,P,Temp,theta_WR,delT)
        P_UR=Prain+Qmelt #calculating input to unsaturated region??
        Scurrent_UR,Eact,Q=UR_ResExp(Sini_UR,P_UR,Epot,theta_UR,delT)
        Svec_WR[iT]=Scurrent_WR
        Svec_UR[iT]=Scurrent_UR       
        EactVec[iT]=Eact
        Qvec[iT]=Q
    return Qvec,EactVec,Svec_WR,Svec_UR
# snow reservoir degree day
def WR_ResExp(Sini,P,Temp,theta,delT):
    Kmlt=theta[0]
    Tthr=theta[1]
    # precipitaiton falling as snow
    if Temp<=Tthr:
        Psnow=P
        Prain=0.0
        S=Sini+Psnow*delT
        Qmelt=0.0
    # precipitation falling as rain
    else:
        Psnow=0.0
        Prain=P
        Qmelt=min(Kmlt*Temp*Sini,Sini/delT)
        S=Sini-Qmelt*delT #This updates the snow storage S by subtracting the amount of snow that has melted during the time step (Qmelt * delT)
    return S,Prain,Qmelt

# soil reservoir Manabe bucket
def UR_ResExp(Sini,P,Epot,theta,delT):
    Smax=theta[0]
    # effective rainfall and residual evaporation
    if P>=Epot:
        Peff=P-Epot
        Eact=Epot
        S=min(Sini+Peff*delT,Smax)
        Q=max(Peff-(S-Sini)/delT,0.0)
    else:
        Peff=0.0
        Eres=Epot-P
        S=max(Sini-Eres*delT,0.0) #Eres??? whats the physical definition behind it.
        Eact=-(S-Sini)+P
        Q=0.0
    # percolation
    Sini=S
    k=theta[1]
    S=Sini*np.exp(-k*delT) #decay factor? gives new values of s applying decay factor
    Q=Q+(Sini-S)/delT
    return S,Eact,Q

# linear reservoir
def linResEv(Sini,P,Epot,theta,delT):
    k=theta[0]
    expTerm=np.exp(-k*delT)
    Emax=k*Sini*expTerm/(1-expTerm)
    Eact=min(Emax+P,Epot)
    PEdiff=P-Eact
    S=(PEdiff/k)+(Sini-PEdiff/k)*np.exp(-k*delT)
    roundZeroEps=1.e-9
    if -roundZeroEps<=S<0:
        S=0.0
    return S,Eact
