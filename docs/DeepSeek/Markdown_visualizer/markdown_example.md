### What?

If you see it somthing goes wrong...

### 1. The Magic of Ratios (Canceling the Scale)

The dot product calculates the true perpendicular distance to the line *multiplied* by the length of the normal vector.

Let's say the true physical distance from the `curr` point to the line is $D_1$, and for the `next` point, it is $D_2$. Let the length of the normal vector be $L$.
The algorithm calculates:

* `currDist` = $D_1 \cdot L$
* `nextDist` = $D_2 \cdot L$

When the code calculates `t`, it divides them:


$$t = \frac{D_1 \cdot L}{(D_1 \cdot L) - (D_2 \cdot L)}$$

Because $L$ is multiplied in every single term, it entirely cancels out of the equation:


$$t = \frac{D_1}{D_1 - D_2}$$

This is why the algorithm doesn't bother doing the heavy math (square roots) required to normalize the vector. The "fake" scale factor destroys itself during the divis
ion, leaving behind a mathematically pure ratio.

