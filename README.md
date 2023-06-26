# FDpy
The purpose of this library is to solve any linear partial differential equation using an implicite finite difference scheme on a one dimensional domain. The library covers a wide range of boundary/initial conditions since both can be specified as equations in function of inner/previous nodes (more details in demo.ipynb file). The problem to be solved is as follows:
$$a_0+a_1U+a_2U_x+a_3U_{xx}+...=b_0+b_1U+b_2U_t+b_3U_{tt}+...$$
Where subscript $x$ and $t$ mean derivative in space and time respectively and $a$ s and $b$ s are constants. The boundary conditions can be specified as a function of other points as follows for example:
$$U(x=0)= c_1+c_2U(x=\Delta x)+c_3U(x=2\Delta x)$$
Where $c$ s are constants. Initial conditions can be defined in the same way.
# Installation
pip install FDpy
# Content
The library first includes the finite difference solver which automatically chooses the finite difference scheme based on the specified order of the equation and accuracy needed (following [1]).
Second, the library also includes a post-processing module where solutions can be animated and compared to the theoritcal solution if available.
Third, a symbolic tree is used to display and evaulate the finite difference scheme for any order. This provides more flexibility, especially in providing initial conditions for isntance.
## References
<a id="1">[1]</a> 
Fornberg, Bengt. (1988). 
Generation of finite difference formulas on arbitrarily spaced grids. 
Mathematics of computation 51.184, p:699-706.
