#let script-size = 7.97224pt
#let footnote-size = 8.50012pt
#let small-size = 9.24994pt
#let normal-size = 10.00002pt
#let large-size = 11.74988pt


#let LNCS-paper(
  title: "Paper title",

  subtitle: "Paper subtitle",

  university: "University of Somewhere",
  email_type: "university.com",
  group: "Group XX",

  authors: (),

  // article's abstract (can be omitted)
  abstract: none,

  // paper size (also affects the margins)
  paper-size: "us-letter",

  bibliography-file: none,
  bibliography-full: false,

  // the document's content
  body,
) = {

  let names = authors.map(author => author.name)
  let author-string = if authors.len() == 2 {
    names.join(" e ")
  } else {
    names.join(", ", last: ", e ")
  }

  let emails = "{" + authors.map(author => author.number).join(", ") + "}@" + email_type

  // metadata
  set document(title: title, author: names)

  // LaTeX font.
  set text(size: normal-size, font: "New Computer Modern")

  // configure the page
  set page(
    paper: paper-size,
    // margins depend on the paper size
    margin: if paper-size != "a4" {
      (
        top: (116pt / 279mm) * 100%,
        left: (126pt / 216mm) * 100%,
        right: (128pt / 216mm) * 100%,
        bottom: (94pt / 279mm) * 100%,
      )
    } else {
      (
        top: 117pt,
        left: 118pt,
        right: 119pt,
        bottom: 96pt,
      )
    },

    header-ascent: 14pt,
    header: locate(loc => {
      let i = counter(page).at(loc).first()
      if i == 1 { return }
      set text(size: script-size)
      grid(
        columns: (6em, 1fr, 6em),
        if calc.even(i) [#i],
        align(center, upper(
          if calc.odd(i) { title } else { author-string }
        )),
        if calc.odd(i) { align(right)[#i] }
      )
    }),

    footer-descent: 12pt,
    footer: locate(loc => {
      let i = counter(page).at(loc).first()
      if i == 1 {
        align(center, text(size: script-size, [#i]))
      }
    })
  )

  // headings
  set heading(numbering: "1.")
  show heading: it => {

    let number = if it.numbering != none {
      counter(heading).display(it.numbering)
      h(7pt, weak: true)
    }

    set text(size: normal-size, weight: 400)
    if it.level == 1 {
      set text(size: normal-size)
      [
        #v(25pt, weak: true)
        #number
        #let styled = { strong }
        #styled(it.body)
        #v(normal-size, weak: true)
      ]
      counter(figure.where(kind: "theorem")).update(0)
    } else {
      v(15pt, weak: true)
      number
      if it.level == 2 {
        strong(it.body)
      } else {
        it.body
      }
      h(7pt, weak: true)
    }
  }

  // lists and links
  set list(indent: 24pt, body-indent: 5pt)
  set enum(indent: 24pt, body-indent: 5pt)
  show link: set text(font: "New Computer Modern Mono")

  // equations
  show math.equation: set block(below: 8pt, above: 9pt)
  show math.equation: set text(weight: 400)

  // citation and bibliography styles
  set bibliography(style: "springer-mathphys", title: "References")

  // theorems
  show figure.where(kind: "theorem"): it => block(above: 11.5pt, below: 11.5pt, {
    strong({
      it.supplement
      if it.numbering != none {
        [ ]
        counter(heading).display()
        it.counter.display(it.numbering)
      }
      [.]
    })
    emph(it.body)
  })

  // display title and authors
  v(35pt, weak: true)
  align(center, {
    text(size: large-size, weight: 700, title)
    v(15pt, weak: true)
    text(size: normal-size, weight: 400, subtitle)
    v(15pt, weak: true)
    text(size: small-size, university)
    v(5pt, weak: true)
    text(size: footnote-size, author-string)
    v(5pt, weak: true)
    text(size: footnote-size, emails)
    v(10pt, weak: true)
    text(size: normal-size, weight: 400, group)
  })

  // display abstract
  if abstract != none {
    v(25pt, weak: true)
    set text(script-size)
    show: pad.with(x: 35pt)
    smallcaps[Abstract.  ]
    abstract
  }

  // display contents.
  v(29pt, weak: true)
  body

  // display bibliography
  if bibliography-file != none {
    v(25pt, weak: true)
    show bibliography: set text(8.5pt)
    show bibliography: pad.with(x: 0.5pt)
    bibliography(bibliography-file, full: bibliography-full)
  }

  show: pad.with(x: 11.5pt)
  set par(first-line-indent: 0pt)
  set text(7.97224pt)

}

#let theorem(body, numbered: true) = figure(
  body,
  kind: "theorem",
  supplement: [Theorem],
  numbering: if numbered { "1" },
)

#let proof(body) = block(spacing: 11.5pt, {
  emph[Proof.]
  [ ] + body
  h(1fr)
  box(scale(160%, origin: bottom + right, sym.square.stroked))
})