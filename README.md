# FDpy
The purpose of this library is to solve any linear partial differential equation using an implicit finite difference scheme on a one dimensional domain. The library covers a wide range of boundary/initial conditions since both can be specified as equations in function of inner/previous nodes (more details in demo.ipynb file). The problem to be solved is as follows:
$$a_0+a_1U+a_2U_x+a_3U_{xx}+...=b_0+b_1U+b_2U_t+b_3U_{tt}+...$$
Where subscript $x$ and $t$ mean derivative in space and time respectively and $a$ s and $b$ s are constants. The boundary conditions can be specified as a function of other points as follows for example:
$$U(x=0)= c_1+c_2U(x=\Delta x)+c_3U(x=2\Delta x)$$
Where $c$ s are constants. 
Very important note: Even though both boundary/intial conditions will be specified using a list of tuples, the tuples mean different things!
On the one hand, boundary conditions can not depend on each others in the library. In other words, if both $U(x=0)$ and $U(x=\Delta x)$ are to be specified, we can define both of these as a function of a constant, U(x=2\Delta x), U(x=3\Delta x),...
In other words, both of these will be represented by a tuple where the first entry multiplies a constant, the second entry multiplies U(x=2\Delta x), etc..
On the other hand, initial conditions usually do not depend on inner points. However, these can depend on each others (for example when a first derivative in time is specified). Accordingly, 
these can also be defined as tuples, but this time in function of each others as follows:
$$U(t=0)= c_1+c_2U(t=0)+c_3U(x=2\Delta t)$$
Where the user can specify as many tuples as they want. The program will make sure that the system of equations is well define and will raise an error if it is over/underdefined.

# Installation
pip install git+https://github.com/JadM133/FDpy.git 
# Content
The library first includes the finite difference solver which automatically chooses the finite difference scheme based on the specified order of the equation and accuracy needed (following [1]).
Second, the library also includes a post-processing module where solutions can be animated and compared to the theoritcal solution if available.
Third, a symbolic tree is used to display and evaulate the finite difference scheme for any order. This provides more flexibility, especially in providing initial conditions for isntance.
## References
<a id="1">[1]</a> 
Fornberg, Bengt. (1988). 
Generation of finite difference formulas on arbitrarily spaced grids. 
Mathematics of computation 51.184, p:699-706.
