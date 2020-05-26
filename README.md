# SEIQRDplot
SEIR interactive plotting with ability to reduce interaction term
<p>dS/dT = -&beta;SI/N<br><br>dE/dt = &beta;SI/N – &alpha;E<br><br>dI/dT =  &alpha;E – [(&phi;&gamma;I) + (&lambda;(1 - &phi;)I)<br><br>dQ/dt = &phi;&gamma;I - &delta;Q<br><br>dR/dt = &delta; + &lambda;(1 - &phi;)I<br><br> where S = Susceptible, E = Exposed, I = Infective (able to infect others), Q = Quarantined (removed from the Infective general population), and R = Recovered (no longer infective, either survived or deceased).<p>N (population size) set at 10000.<p> Solved via semi-implicit Euler method (see <a href="https://towardsdatascience.com/social-distancing-to-slow-the-coronavirus-768292f04296">Hobbs, 2020</a>).
