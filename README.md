# loopbode
## Introduction
There are two scripts in this project.  
The script `loopbode_generator_gui.py` is used to generate the data about the bode plot according to the given poles and zeros for test.  
The script `loopbode_analysis_gui.py` is used to extract the poles and zeros from the given bode plot data.

The pole and zero are described by 3 parameter: $log_{10}f$, $\xi_{i}$, and $a_{i}$.  

$log_{10}f\in\mathbf{R}$  
$\xi_{i}\in[-1,+1]$  
$a_{i}=\pm1, \pm0.5$  
  
|Pole/zero description table||
|-|-|
|$a_{i}=+0.5$, $\xi_{i}=+1.0$|Left-plane 1-order zero|
|$a_{i}=+0.5$, $\xi_{i}=-1.0$|Right-plane 1-order zero|
|$a_{i}=-0.5$, $\xi_{i}=+1.0$|Left-plane 1-order pole|
|$a_{i}=-0.5$, $\xi_{i}=-1.0$|Right-plane 1-order pole|
|$a_{i}=+1.0$, $\xi_{i}\in(0,+1.0)$|A pair of left-plane 2-order zeros|
|$a_{i}=+1.0$, $\xi_{i}\in(-1.0,0)$|A pair of right-plane 2-order zeros|
|$a_{i}=-1.0$, $\xi_{i}\in(0,+1.0)$|A pair of left-plane 2-order poles|
|$a_{i}=-1.0$, $\xi_{i}\in(-1.0,0)$|A pair of right-plane 2-order poles|
|$a_{i}=+1.0$, $\xi_{i}=0$|A pair of 2-order zeros in the imaginary axes|
|$a_{i}=-1.0$, $\xi_{i}=0$|A pair of 2-order poles in the imaginary axes|
  
## Principle
All the transfer function of a real system has the real-number coefficients. Therefore, its numerator and denominator can be converted to the multiplication of 1-order and 2-order polynomial of `s`, which means all real system can be converted to the cascode of 1-order and 2-order systems. 

To be continuous...
