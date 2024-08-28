from soundevent.data.terms import Term


def term_from_key(key: str) -> Term:
    """Create a simple term from a string.

    Parameters
    ----------
    key : str
        Key to create a term from.

    Returns
    -------
    term : Term
        Term object.

    Notes
    -----
    Previously, `soundevent` data objects such as Tag and Feature
    did not use the Term class. This function creates a simple term
    from a string to be used in those objects.

    We recommend using the Term class for new code. This makes
    it easier to ensure terms are consistent across codebases and
    data formats.

    """
    return Term(
        label=key,
        name=f"soundevent:{key}",
        definition="Unknown",
    )


def key_from_term(term: Term) -> str:
    return term.label
