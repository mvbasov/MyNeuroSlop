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

If you see this something goes wrong... This page is a standalone Markdown + KaTeX viewer built with HTML/JS. It fetches a Markdown file (hardcoded or via `?file.md` query), renders it using **marked.js** (CDN + local fallback), and processes LaTeX math with **KaTeX** (CDN + local fallback). The page is versioned (1.2.0) and displays a small footer.

**Features**
- Loads Markdown from a default URL or user-supplied query parameter.
- Full GitHub-flavoured Markdown (tables, code blocks, etc.).
- Renders inline `$...$` and display `$$$`...$$`$` math using KaTeX.
- No external dependencies are required – the page loads all libraries dynamically.
- Works best when served from an HTTP server (e.g., `python -m http.server`).

**Markdown examples**
- **Bold** and *Italic*
- [Hyperlink to Example](https://example.com)
- `inline code`

 ```python
print("Hello, world!")
```

**KaTeX examples**
- Inline: $E = mc^2$
- Display: $$ \displaystyle \int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2} $$
- Vector: $\vec{F} = m\\vec{a}$
- Matrix: $$ \begin{pmatrix} a & b \\ c & d \end{pmatrix} $$

$$ \text{File}_{B} = \text{File}_{A} + \text{Diff}_{A \to B} $$

* `nextDist` = $D_2 \cdot L$

$$ \text{Target} < \text{Anchor} \implies \text{Anchor} - \text{Diff}_{T \to A} = \text{Target} $$
$$ \text{Target} > \text{Anchor} \implies \text{Anchor} + \text{Diff}_{A \to T} = \text{Target} $$

* `currDist` = $D_1 \cdot L$
