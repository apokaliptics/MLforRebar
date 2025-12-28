---
title: "Lattice-based access control"
source: "https://en.wikipedia.org/wiki/Lattice-based_access_control"
---

In [computer security](/wiki/Computer_security "Computer security"), **lattice-based access control** (**LBAC**) is an [access control](/wiki/Access_control "Access control") model defined to control data transfers between **objects** (such as resources, computers, and applications) and **subjects** (such as individuals, groups or organizations). Subjects and objects will be collectively called 'the entities' and the model is valid even if there is not a distinction between subjects and objects.

Entities are given unique *labels*, on which a *dominance* relation *≤* is defined. *Data can move among entities according to the dominance relation between their labels.* For example, one can define *Public* *≤* *Confidential* and so if database *A* is labeled *Public* and database *B* is labeled *Confidential*, data from *A* can move to *B*. Further, this theory postulates that the set of permissible labels must form a *lattice*, i.e., a partially ordered set where for each two labels there are a unique label that dominates them both (their *join*) and a unique label that both of them dominate (their *meet*).

Lattice based access control models were first formally defined by [Denning](/wiki/Dorothy_E._Denning "Dorothy E. Denning") (1976); see also Sandhu (1993).

More recent research has shown that the condition that the partial order of labels must form a lattice unnecessarily limits the power of the model. If this condition is removed, the model becomes simpler and more general. It can be proved that this more general model can define the same data flows as other security models, such as Access Control Lists, Discretionary Access Control, Role-based Access Control, Attribute-based Access Control. This model can also be implemented in network routing, by establishing a correspondence between labels and network addresses. However, this second, more general, access control model can no longer be called Lattice-based Access Control and so it appears that this model has become obsolete. Note that it is possible to complete any partial order of entities to make it a lattice, however this is unnecessary.

A short ArXiv paper discussing the history of this concept is Logrippo (2025). It contains references to several journal and conference papers.

## See also

[[edit](/w/index.php?title=Lattice-based_access_control&action=edit&section=1 "Edit section: See also")]

* [Access control list](/wiki/Access_control_list "Access control list")
* [Attribute-based access control](/wiki/Attribute-based_access_control "Attribute-based access control") (ABAC)
* [Bell–LaPadula model](/wiki/Bell%E2%80%93LaPadula_model "Bell–LaPadula model")
* [Biba Model](/wiki/Biba_Model "Biba Model")
* [Capability-based security](/wiki/Capability-based_security "Capability-based security")
* [Computer security model](/wiki/Computer_security_model "Computer security model")
* [Context-based access control](/wiki/Context-based_access_control "Context-based access control") (CBAC)
* [Discretionary access control](/wiki/Discretionary_access_control "Discretionary access control") (DAC)
* [Graph-based access control](/wiki/Graph-based_access_control "Graph-based access control") (GBAC)
* [Lattice (order)](/wiki/Lattice_(order) "Lattice (order)")
* [Mandatory access control](/wiki/Mandatory_access_control "Mandatory access control") (MAC)
* [Organisation-based access control](/wiki/Organisation-based_access_control "Organisation-based access control") (OrBAC)
* [Risk-based authentication](/wiki/Risk-based_authentication "Risk-based authentication")
* [Role-based access control](/wiki/Role-based_access_control "Role-based access control") (RBAC)
* [Rule-set-based access control (RSBAC)](/wiki/RSBAC "RSBAC")

## References

[[edit](/w/index.php?title=Lattice-based_access_control&action=edit&section=2 "Edit section: References")]

* [Denning, Dorothy E.](/wiki/Dorothy_E._Denning "Dorothy E. Denning") (1976). ["A lattice model of secure information flow"](http://faculty.nps.edu/dedennin/publications/lattice76.pdf) (PDF). *[Communications of the ACM](/wiki/Communications_of_the_ACM "Communications of the ACM")*. **19** (5): 236–243. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1145/360051.360056](https://doi.org/10.1145%2F360051.360056).
* Logrippo, Luigi (2025). "Security theory for data flow and access control: From partial orders to lattices and back, a half-century trip." arXiv:2509.10727.
* Sandhu, Ravi S. (1993). ["Lattice-based access control models"](http://www.winlab.rutgers.edu/~trappe/Courses/AdvSec05/access_control_lattice.pdf) (PDF). *[IEEE Computer](/wiki/IEEE_Computer "IEEE Computer")*. **26** (11): 9–19. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[1993Compr..26k...9S](https://ui.adsabs.harvard.edu/abs/1993Compr..26k...9S). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1109/2.241422](https://doi.org/10.1109%2F2.241422).

* [v](/wiki/Template:Computer-security-stub "Template:Computer-security-stub")
* [t](/wiki/Template_talk:Computer-security-stub "Template talk:Computer-security-stub")
* [e](/wiki/Special:EditPage/Template:Computer-security-stub "Special:EditPage/Template:Computer-security-stub")