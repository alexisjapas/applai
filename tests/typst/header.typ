#let date = datetime.today()

#[
  #set text(
    size: 16pt,
    weight: "bold"
  )
  #smallcaps(include "content/name.typ")
]
#h(1fr)
#date.display("[day]/[month]/[year]")
\
#include "content/email.typ"
\
#include "content/phone.typ"