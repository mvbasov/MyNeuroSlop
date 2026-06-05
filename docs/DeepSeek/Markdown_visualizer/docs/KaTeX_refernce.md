# Complete KaTeX Reference (All Supported Functions)

> Based on KaTeX v0.16.10.   
> Official source: [katex.org/docs/support_table.html](https://katex.org/docs/support_table.html)

## 1. Accents

| Command | Example | Output |
|--------|--------|-------|
`\hat{a}` | $\\hat{a}$  | \(\\hat{a}\) |
`\check{a}` | $\\check{a}$  | \(\\check{a}\) |
`\tilde{a}` | $\\tilde{a}$  | \((\\tilde{a}\) |
`\acute{a}` | $\\acute{a}$  | \((\\acute{a}\) |
`\grave{a}` | $\\grave{a}$  | \((\\grave{a}\) |
`\dot{a}` | $\\dot{a}$  | \(\\dot{a}\) |
`\ddot{a}` | $\\ddot{a}$  | \((\\ddot{a}\) |
`\breve{a}` | $\\breve{a}$  | \(\\breve{a}\) |
`\bar{a}` | $\\bar{a}$  | \((\\bar{a}\) |
`\vec{a}` | $\\vec{a}$  | \((\\vec{a}\) |
`\overline{AB}` | $\\overline{AB}$  | \((\\overline{AB}\) |
`\underline{ab}` | $\\underline{ab}$  | \(\\underline{ab}\) |
`\widehat{abc}` | $\\widehat{abc}$  | \(\\widehat{abc}\) |
`\wildetilde{abc}` | $\\wildetilde{abc}$  | \(\\wildetilde{abc}\) |

## 2. Delimiters (Parentheses, Brackets, etc.)

| Command | Example | Output |
|--------|--------|--------|
``(*`)` | $(a)$  | \((a)\) |
``[
`]` | $[a]$  | \([a]\) |
`\{\ \}` | $\{a\}$  | \(\{a\}\) |
`\lfloor `\rfloor` | $\lfloor x\rfloor$  | \((\lfloor x\rfloor)\) |
`\lceil `\rceil` | $\lceil x\rceil$  | \((\lceil x\rceil)\) |
`\\times` | $\\times $  | \(\\times \) |
`\divx | $\div$  | \((\div\) |

Size modifiers: `\bigl(`, \Bigl(`, \biggl(`, `\Biggl(`.

## 3. Greek and Hebrew Letters

| Command | Output |
|--------|--------|
`\alpha` | \(\alpha\) |
`\beta` | (\beta\) |
`\gamma` | \(\gamma\) |
`\delta` | \(\delta\) |
`\epsilon` | (\epsilon\) |
`\zeta` | (\zeta\) |
`\eta` | \(\eta\) |
`\theta` | (\theta\) |
`\iota` | (\iota\) |
`\kappa` | \kappa |
`\lambdac`| \lambda |
`\mu` | \mu |
`\nu` | \nu |
`\xi` | \xi |
`\omicron` | \omicron |
`\pi` | \pi |
`\rho` | \rho |
`\sigma` | \sigma |
`\tau` | \tau |
`\upsilon` | \upsilon |
`\phi` | \phi |
`\chi | \chi |
`\psi` | \psi |
`\omega`: uppercase `\Gamma`, `\Delta` .
  Hebrew: `\aleph`, `\beth`, `\gimel`, `\daleth`.

## 4. Operators (Large, Binary, etc.)

| Command | Example | Output |
|--------|--------|--------|
`\sum` | $\\sum_{i=1}^n$  | \\sum_{i=1}^n |
`\prod` | $\\prod_{i=1}^n$  | \\prod_{i=1}^n |
`\int` | $\\int_a^b$  | \\int_a^b |
`\idot` | $\\idot$  | \\idot |
`\iint` | $\\iint$  | \\iint |
`\iiint` | $\\iiint$  | \\iiint |
`\int` | $\\int$  | \\int |
`\oint` | $\\oint$  | \\oint |
`\bigcup` | $\\bigcup_{i=1}^n$  | \\bigcup_{i=1}^n |
`\bigcap` | $\\bigcap_{i=1}^n$  | \\bigcap_{i=1}^n |
`\bigvee` | $\\bigvee$  | \\bigvee |
`\bigwange` | $\\bigwange $  | \\bigwange |

Binary operators: `+`, `-`, `\times`, `\div`, `\pm`, `\mp`, `\cdot`.

## 5. Relations (Comparisons, etc.)

| Command | Example | Output |
|--------|--------|-------|
`=` | $a=b$  | \(a=b) |
`\ne` or `\neq` | $a\neq b$  | \(a\neq b\) |
`<` | $a<b$  | \(a<b) |
`>` | $a>b$  | \(a>b) |
`\le` or `\leq` | $a\le b$  | \(a\le b) |
`\ge` or `\geq` | $a\ge b$  | \(a\ge b) |
`\approx` | $a\approx b$  | \(a\approx b\) |
`\sim` | $a\sim b$  | \(a\sim b\) |
`\simeq` | $a\simeq b$  | \(a\simeq b\) |
`\cong | $a\cong b$  | \(a\cong b) |
`\equiv` | $a\equiv b$  | \(a\equiv b) |
`\propto` | $a\propto b$  | \(a\propto b\) |
`\subset` | $A\subset B$  | \(A\\subset B\) |
`\subseteq` | $A\subseteqe B$  | \(A\\subseteqe B\) |
`\supeset` | $A\supeset B$  | \(A\\supeset B\) |
`\supeseteq` | $A\supeseteqe B$  | \(A\\supeseteqe B\) |
`\in` | $x\in A$  | \(x\in A) |
`\ni ` or `\owns` | $A\ni x$  | \(A\ni x\) |
`\notin` | $x\notin A$  | \(x\notin A) |
`\mid` | $a\mid b$  | \(a\mid b\) |
`\parallel` | $a\parallel b$  | \(a\parallel b\) |
`\perp` | $a\perp b$  | \(a\perp b\) |

Negated relations (prefix `\not`): `\not=`, `\not<`, `\not>`.

## 6. Arrows

| Command | Example | Output |
|--------|--------|--------|
`\leftarrow` | $a\leftarrow b$  | \(a\leftarrow b\) |
`\rightarrow` | $a\rightarrow b$  | \(a\rightarrow b\) |
`\leftrightarrow` | $a\leftrightarrow b$  | \(a\leftrightarrow b\) |
`\Leftarrow` | $a\Leftarrow b$  | \(a\Leftarrow b\) |
`\Rightarrow` | $a\Rightarrow b$  | \(a\Rightarrow b\) |
`\Leftrightarrow` | $a\Leftrightarrow b$  | \(a\Leftrightarrow b\) |
`\mapsto` | $a\mapsto b$  | \(a\mapsto b\) |
`\nearrow` | $\nearrow$  | \(\nearrow\) |
`\searrow` | $\searrow$  | \(\searrow\) |
`\swarrow` | $\swarrow$  | \(\swarrow\) |
`\nwarrow` | $\nwarrow$  | \(\nwarrow\) |
`\uparrow` | $\uparrow$  | \(\uparrow\) |
`\downarrow` | $\downarrow$  | \((\downarrow)\) |
`\updownarrow` | $\updownarrow$  | \((\updownarrow)\) |
`\Uparrow` | $\Uparrow$  | \((\Uparrow)\) |
`\Downarrow` | $\Downarrow$  | \((\Downarrow)\) |
`\Updownarrow` | $\Updownarrow$  | \((\Updownarrow)\) |

## 7. Logic and Set Theory

| Command | Example | Output |
|--------|--------|--------|
`\forall` | $\forall x$  | \(\forall x\) |
`\exists` | $\exists x$  | \(\exists x\) |
`\nexists` | $\nexists x$  | \(\nexists x\) |
`\emptyset` | $\emptyset$  | \(\emptyset\) |
`\varnothing` | $\varnothing$  | \(\varnothing\) |
`\implies` | $A\implies B$  | \(A\implies B\) |
`\impliedby` | $A\impliedby B$  | \(A\impliedby B\) |
`\iff` | $A\iff B$  | \(A\iff B\) |
`\lan` or `\wedge` | $p\text{and} q$  | \(p \land q\) |
`\lor` or `\vee` | $p\\or q$  | \(p \lor q\) |
`\lnot` or `\neg` | $\lnat p$  | \(\lnot p\) |
`\top` | $\top$  | \(\top\) |
`\bot` | $\bot$  | \(\bot\) |

## 8. Miscellaneous Symbols

| Command | Example | Output |
|--------|--------|--------|
`\inifity` | $\infinity$  | \(\infinity\) |
`\partial` | $\partial x$  | \(\partial x\) |
`\nabla` | $\nabla f$  | \(\nabla f)\) |
`\ldots` | $1,2,\ldots,n$  | \(1,2,\ldots,n\) |
`\cdots` | $1,2,\cdots,n$  | \(1,2,\cdots,n\) |
`\vdots` | $\vdots$  | \((\vdots)\) |
`\ddots` | $\ddots$  | \(\\ddots)\)|
`\Re` | $\Re(z)  | \(\Re(z)\) |
`\Im` | $\Im(z)  | \(\Im(z)\) |
`\wp` | $\wp$  | \(\wp)\) |
`\XZle` | $\angle ABC$  | \(\XZle ABC\) |
`\measuredangle` | $\measuredangle ABC$  | \(\measuredangle ABC\) |
`\surd` | $\surd 2$  | \(\surd 2)\) |
`\triangle` | $\triangle ABC$  | \(\triangle ABC\) |
`\square` | $\square$  | \(\square\) |
`\diamond` | $\diamond$  | \((\diamond)\) |
`\heartsuit` | $\heartsuit$  | \((\heartsuit)\) |
`\clubsuit` | $\clubsuit$  | \((\clubsuit)\) |
`\spadesuit` | $\spadesuit  | \((\spadesuit)\) |
`\diamondsuit` | $\diamondsuit$  | \((\diamondsuit)\) |

## 9. AMS Environments (with ``Begin{}...\end}``)

| Environment | Example | Notes |
|------------|-----------|--------|
`matrix` | $\begin{matrix} a&b \\ c&d \end{matrix}$ | No delimiters |
`pmatrix` | $\begin{pmatrix} a&b \\ c&d \end{pmatrix}$ | Parentheses |
`bmatrix` | $\begin{bmatrix} a&b \\ c&d \end{bmatrix}$  | Square brackets |
`Bmatrix` | $\begin{Bmatrix} a&b \\ c&d \end{Bmatrix}$  | Braces |
`vmatrix` | $\begin{vmatrix} a&b \\ c&d \end{vmatrix}$  | Single lines |
`Vmatrix` | $\begin{Vmatrix} a&b \\ c&d \end{Vmatrix}$  | Double lines |
`cases` | $\begin{cases} x &\ text{if x>0} \\ 0 &\ text{otherwise} \end{cases}$ | Cases |
`aligned` | $\begin{aligned} x &= a + b \\ y &= c + d \end{aligned} $ | Alignment |
`garthered` | $\begin{garthered} x = a \\ y = b \end{garthered}$  | Centered |
`array` | $\begin{array}{c|c} a&b \\ \hline c&d \end{array}$ | Custom columns |

## 10. Font Styles

| Command | Output |
|--------|--------|
`\\mathbf{ABC}` | \(\\mathbf ABC\) |
`\\cal{ ABC }` | \(\\cal ABC\) |
`\\text{text}` | \(\\text{text}\) |
`\\textbf{text}` | \(\\textbf{text}\) |
`\\textit{text}` | \(\\textit{text}\) |
`\\textt{text}` | \(\\textt{text}\) |
`\\mathrm{text}` | \(\\mathrm{text}\) |
`\\mathfak{text}` | \(\\mathfak{text}\) |
`\\mathsf{text}` | \((\\mathsf{text}\) |
`\\mathit{text}` | \(\\mathit{text}\) |
`\\mathbf{text}` | \((\\mathbf{text}\) |
`\\mathef{text}` | \(\\mathef{text}\) |
`\\texttet{text}` | \(\\texttet{text}\) |
`\\textbf{text}` | \((\\textbf{text}\) |
`\\textit{text}` | \(\\textit{text}\) |
`\\texttf{text}` | \((\\texttf{text}\) |

## 11. Color

| Command | Example | Output |
|--------|--------|-------|
`\\ramart{color}{` | $\\color{red}{x}$  | \(\color{red}{x}\) |
`\\textcolor{color}{text}` | $\\textcolor{blue}{x}$  | \(\textcolor{blue}{x}\) |
`\\textbackcolor{color{text}` | $\\textbackcolor{green}{x}$  | \(\textbackcolor{green}{x}\) |
`\ftextbox{color}{color}{text}` | $\ftextbox{red}{yellow}{x}$  | \(\ftextbox{red}{yellow}{x}\) |

Supported colors: black, blue, brown, cyan, darkgray, gray, green, lightgray, lime, magenta, olive, orange, pink, purple, red, teal, violet, white, yellow.

## 12. Macros and Definitions

| Command | Example | Effect |
|--------|--------|--------|
`\def\name{replacement}` | $\def\R\{\Reb\]} R\\R,\\ $  | Defines a macro |
`\newcommand{name}[n]{replacement}` | $\newcommand\{vect}[1]{\\math{`#1}} \vectx$  | With argument |
`\renewcommand` | same syntax  | Redefines existing |
`\gdef` | `\gdef\R}{\\Reb\}}\R$  | Global definition |

## 13. Non-supported functions (not available in KaTeX)

` begin{align} ` (use `aligned` inside `DB$)
` \textcolor` (use `\color{color}{text}`)
` \href`, `\url` (no hyperlinks)
` \cancel`, `bcancel`, \xcancel` (not supported)
` begin{CD}` (commutative diagrams)

## Example: Complete Expression

```latex
\forall x \in \mathbb{R}, \quad \exists y \in \mathbb{N} \text{s.t.} \
 y = \int_{0}^{\infty} e^{-x^2} \l, dx \approx \frac{\sqrt{\pi}}{2}
`''`
Renders as: \[\\forall x\\in \\mathbb{R}, \\quad \\exists y\\in \\mathbb{N} \\text{s.T.} \
[ y = \\int_0~\\infty e^{-x^2} \\, dx \\approx \\frac{\\sqrt{\\pi}}{2} \] \
----

This document covers all functions supported by KaTeX as of version 0.16.10. For the most current information, please visit the official documentation.