# Baby
> Author: Nguyen Quang Vinh

The message is encrypted using the textbook RSA algorithm, and to decrypt the message we need to retrieve the values of the two primes `p` and `q`.

We know the value of `r * p - s * q`, let the value be `a`. We have this observation that `r > s`, and `a < 0`, hence `p < q`. Let `q = p + b`, we have
```
r * p - s * q = a
<=> r * p - s * (p + b) = a
<=> r * p - s * p - s * b = a
<=> (r - s) * p - s * b = a
<=> (r - s) * p = s * b + a
```
Hence, `s * b + a` is divisible to `r - s`. Finding `b` is a linear congruence problem and the algorithm for solving this can be found on Stackoverflow. The snippet that I used is in the commented out code. The value of `b` underneath is the value calculated from the function. `b` has a restriction to be 1024 bits so we can use the particular solution, as any of the other solutions in the general solution set is `4096` bits long.

Having the value of `b`, we can retrieve the value of `p` by doing simple division. `divmod` is used here since it can handle division with big integers. `q` is derived from `q = p + b`. From `p` and `q`, we can figure out the inverse of e, `d`, and use this to retrieve the flag.

The script is in the `solve.py` file.