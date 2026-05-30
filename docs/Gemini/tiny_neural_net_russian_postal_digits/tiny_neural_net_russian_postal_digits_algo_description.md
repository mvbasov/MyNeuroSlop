I’d love to break down exactly how the `TinyNN` engine works.

`TinyNN` is a custom-built, vanilla JavaScript implementation of a classic **Feed-Forward Multi-Layer Perceptron (MLP)**. It uses **Supervised Learning** via **Stochastic Gradient Descent (SGD)** and **Error Backpropagation**. Because it is written from scratch without huge libraries like TensorFlow, it perfectly exposes the raw, beautiful math of how machines learn.

Let’s dissect its operation step-by-step, exactly as it executes in our code.

---

### 1. The Architecture & Initialization

When we call `new TinyNN(9, 6, 11)`, we are building a 3-layer network:

* **Input Layer (9 nodes):** One for each of the 9 segments in our Russian postal grid. (0 or 1).
* **Hidden Layer (6 nodes):** The "brain" where the network learns abstract combinations of lines.
* **Output Layer (11 nodes):** The final guess (Digits 0-9, plus NaN).

**The Blank Slate:**
When the class initializes, it creates arrays for **Weights** (connections between nodes) and **Biases** (internal offsets for nodes). It fills these with random numbers between `-1.0` and `1.0`.
At this point, the network knows absolutely nothing. If you ask it to guess a number, it will output random noise.

---

### 2. Forward Propagation (`predict` method)

Forward propagation is how the network takes an input drawing and makes a guess. It calculates the values layer by layer moving forward.

**A. Hidden Layer Calculation:**
For every single one of the 6 hidden neurons, the network does a sum of all 9 inputs multiplied by the weights of the lines connecting them, plus the hidden neuron's bias:


$$Sum = Bias + (Input_0 \times Weight_{0}) + (Input_1 \times Weight_{1}) ...$$

It then passes this raw sum through the **Sigmoid Activation Function** (`1 / (1 + Math.exp(-x))`).

The Sigmoid function elegantly squashes any raw number (whether it is -500 or +1000) into a clean decimal exactly between `0.0` and `1.0`. This becomes the activation level of that hidden neuron.

**B. Output Layer Calculation:**
The exact same math happens again, but this time it treats the 6 activated hidden neurons as its inputs. It multiplies them by the Hidden-to-Output weights, adds the output biases, squashes them through Sigmoid, and spits out 11 final numbers between 0.0 and 1.0.
*Whichever node outputs the highest number (e.g., Node 7 outputs 0.92) is the network's final guess.*

---

### 3. Calculating the Error

To teach the network, we must tell it how badly it messed up. During the `train` method, we provide the network's prediction and the actual **Target** (a "One-Hot" array where the correct digit is 1, and the rest are 0).

For every output node, we calculate the raw error:


$$Error = Target - Prediction$$


*(If it guessed 0.8 but the target was 1.0, the Error is +0.2. If it guessed 0.6 but the target was 0.0, the Error is -0.6).*

---

### 4. Error Backpropagation (`train` method)

This is the magic trick of neural networks. We now take those Errors and push them *backwards* through the network to figure out which specific weights caused the mistake.

**A. Output Layer Gradients (Deltas):**
To know how to adjust the weights, we calculate a "Delta". The Delta combines the Error with the *derivative* (slope) of the Sigmoid function (`y * (1 - y)`).


$$Delta = Error \times (Prediction \times (1 - Prediction))$$


This calculus tells the network: *"If this neuron was already highly confident (near 1 or 0), don't tweak it too aggressively. If it was unsure (near 0.5), tweak it a lot."*

**B. Hidden Layer Gradients:**
But how do we know the error of a *hidden* neuron? We don't have targets for the hidden layer!
Instead, we backpropagate. A hidden neuron's error is calculated by looking at the output Deltas it connects to, multiplied by the weights of those connections. If a hidden neuron had a strong connection to an output neuron that was very wrong, that hidden neuron takes a large share of the blame.
We then calculate the Hidden Delta using the derivative again.

---

### 5. Updating the Weights (Learning)

Now that every node in the network knows its Delta (how much it needs to change), we finally adjust the connections.

For every single weight, we apply **Stochastic Gradient Descent**:


$$New\_Weight = Old\_Weight + (Activation \times Delta \times Learning\_Rate)$$

* **Activation**: Did this specific pathway even fire? If the input was 0, it didn't contribute to the error, so don't change its weight.
* **Delta**: The direction and magnitude of the required fix.
* **Learning Rate (`this.lr = 0.15`)**: A speed limit. If we change weights too drastically, the network becomes unstable. We just nudge them 15% of the way toward the "correct" value.

By repeating this `predict -> calculate error -> backpropagate -> adjust weights` loop thousands of times (Epochs) across all 512 possible visual patterns, the weights slowly organize themselves. The chaos turns into logic, and `TinyNN` successfully learns how to read Russian postal digits!
