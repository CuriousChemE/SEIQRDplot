import numpy as np
from bokeh.models import ColumnDataSource, FactorRange, Slider, RangeSlider, NumeralTickFormatter, Div, LabelSet, SingleIntervalTicker
from bokeh.plotting import figure
from bokeh.io import output_file, show, curdoc
from bokeh.layouts import column, row, layout
# from bokeh.models import Slider, Label, SingleIntervalTicker, NumeralTickFormatter,RadioButtonGroup, Div

def seiqr_model_with_soc_dist(init_vals, params, t):
    S_0, E_0, I_0, Q_0, R_0 = init_vals
    S, E, I, Q, R = [S_0], [E_0], [I_0], [Q_0], [R_0]
    alpha, beta, gamma, lambdaI, lambdaQu, phi, rho = params
    dt = t[1] - t[0]
    for ct,time in enumerate(t[1:],1):
        next_R = R[-1] + (lambdaQu*Q[-1] + lambdaI*(1-phi)*I[-1])*dt
        next_Q = Q[-1] + (phi*gamma*I[-1] - lambdaQu*Q[-1])*dt 
        next_S = S[-1] - (rho[ct]*beta*S[-1]*I[-1])*dt
        next_E = E[-1] + (rho[ct]*beta*S[-1]*I[-1] - alpha*E[-1])*dt
        next_I = I[-1] + (alpha*E[-1] - (phi*gamma*I[-1]+lambdaI*(1-phi)*I[-1]))*dt
        R.append(next_R)
        Q.append(next_Q)
        S.append(next_S)
        E.append(next_E)
        I.append(next_I)                 
        
    # data = {'t':t,'S':S,'E':E,'I':I,'R':R}
    data = t,S,E,I,Q,R
    # return np.stack([t, S, E, I, R]).T
    return data

# Define parameters
t_max = 150
dt = .1
t = np.linspace(0, t_max, int(t_max/dt) + 1)
# rh=(np.ones(t.size)) ... will use to provide a range of rho values, one per dt, with 3 ranges sliced set by a range slider...
N = 10000
init_vals = 1 - 1/N, 1/N, 0, 0, 0
alpha = 1/5
beta = 1.8
gamma = 1/2
lambdaI = 1/4
lambdaQu = 1/2 # use a delta on the output
phi = 0                         
#rho = 1
rho=(np.ones(t.size))
#rho[10*10:10*60]=.2 # manually drop rho to 0.5 for days 3-60
params = alpha, beta, gamma, lambdaI, lambdaQu, phi, rho
# Run simulation
tt,S,E,I,Q,R = seiqr_model_with_soc_dist(init_vals, params, t)
source = ColumnDataSource(data=dict(t=tt,S=S,E=E,I=I,Q=Q,R=R))

# set up Div with R0, max I, and day of max I
drtext=f"max I = {'{0:.0%}'.format(max(I))} on day {int(tt[I.index(max(I))])}"
divright = Div(text=drtext, sizing_mode="scale_width", style={'font-size': '200%', 'color': 'red'})      

plot = figure(x_range=(0, 150),y_range=(0,1), plot_width=700, plot_height=400,title='SEIQR',tools="")
# need to add colors and legend, get rid of tools
plot.line('t', 'S', source=source, line_width=3, line_alpha=0.6, color="Green",legend="Susceptible")
plot.line('t', 'E', source=source, line_width=3, line_alpha=0.6, color="Cyan",legend="Exposed")
plot.line('t', 'I', source=source, line_width=3, line_alpha=0.6, color="Red",legend="Infective")
plot.line('t', 'Q', source=source, line_width=3, line_alpha=0.6, color="Indigo",legend="Quarantined")                       
plot.line('t', 'R', source=source, line_width=3, line_alpha=0.6, color="Blue",legend="Recovered")
plot.legend.location = "bottom_right"
plot.xaxis.ticker = SingleIntervalTicker(interval=25)
plot.xgrid.ticker = SingleIntervalTicker(interval=25)
plot.xaxis.axis_label = 'Days'
plot.yaxis.ticker = SingleIntervalTicker(interval=0.10)
plot.ygrid.ticker = SingleIntervalTicker(interval=0.10)
plot.yaxis.axis_label = '% of population'
plot.yaxis.formatter = NumeralTickFormatter(format='0 %')

#set up sliders
AlphaSlider = Slider(title="Mean Incubation Days (1/\u03B1)", value=5, start=1, end=10, step=1)
BetaSlider = Slider(title="Interaction Factor (\u03B2)", value=1.8, start=0.1, end=10, step=0.1)
GammaSlider = Slider(title="Mean Days before Quarantine (1/\u03B3)", value=2, start=1, end=10, step=1)
LambdaISlider= Slider(title="Mean Days to Recover (1/\u03BB)", value=4, start=1, end=10, step=1) 
LambdaQSlider= Slider(title="Mean Days to Recover post-Quarantine (1/\u03B4)", value=2, start=1, end=10, step=1)
PhiSlider = Slider(title="Fraction of Infective Quarantined (\u03C6)", value=0, start=0, end=1, step=0.1)                         
# sliders for adjusting beta (by factor rho)
# RhoSlider = Slider(title="Rho", value=1, start=0.1, end=1, step=0.1)
DateSlider=RangeSlider(title="Day range for \u03B2 interaction reduction", value=(30,90), start=1, end=150, step=1)
RhoDuringSlider = Slider(title="\u03B2 reduction factor during range", value=1, start=0.1, end=1, step=0.1)
RhoAfterSlider = Slider(title="\u03B2 reduction factor after range", value=1, start=0.1, end=1, step=0.1)



#set up callback
def update_data(attrname, old, new):
    #reset rho
    rho=(np.ones(t.size))
    # Get the current slider values
    alpha=1/AlphaSlider.value
    beta=BetaSlider.value
    gamma=1/GammaSlider.value
    lambdaI=1/LambdaISlider.value                      
    lambdaQu=1/LambdaQSlider.value
    phi=PhiSlider.value
    range_start = int(DateSlider.value[0])
    range_end = int(DateSlider.value[1])
    # rho=1 # for this version, set rho always equal to 1
    rhotemp=RhoDuringSlider.value
    rhoafter=RhoAfterSlider.value
    rho[10*range_start:10*range_end]=rhotemp
    rho[1+10*range_end:]=rhoafter
    params = alpha, beta, gamma, lambdaI, lambdaQu, phi, rho
    tt,S,E,I,Q,R = seiqr_model_with_soc_dist(init_vals, params, t)
    source.data=dict(t=tt,S=S,E=E,I=I,Q=Q,R=R)
    divright.text=f"max I = {'{0:.0%}'.format(max(I))} on day {int(tt[I.index(max(I))])}"
                                                  

# for w in [AlphaSlider, BetaSlider, GammaSlider, LambdaISlider, LambdaQSlider,PhiSlider, RhoSlider]:
for w in [AlphaSlider, BetaSlider, GammaSlider, LambdaISlider, LambdaQSlider,PhiSlider,DateSlider,RhoDuringSlider, RhoAfterSlider]:
    w.on_change('value', update_data)

# inputs = column(AlphaSlider, BetaSlider, GammaSlider, LambdaISlider, LambdaQSlider,PhiSlider, RhoSlider)
inputs = column(AlphaSlider, BetaSlider, GammaSlider, LambdaISlider, LambdaQSlider,PhiSlider,divright)
inputsright=column(DateSlider, RhoDuringSlider, RhoAfterSlider)

# read in html strings for header and footer
with open ("SEIQRDeq.txt", "r") as myfile:
    texttop=myfile.read()
    
divtop = Div(text=texttop, sizing_mode="scale_width")      

curdoc().add_root(divtop)
curdoc().add_root(row(inputs,plot,inputsright))
curdoc().title = "SEIQRDModel"
