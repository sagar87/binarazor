from math import ceil

import streamlit as st

from config import App
from handler import handle_page_change




def page_selectbox(key, num_items, page_size): 
    location = st.sidebar.empty()
    # Display a pagination selectbox in the specified location.
    num_pages = ceil(num_items / page_size)
    
    _ = location.selectbox(
        "Select page",
        range(num_pages),
        format_func=lambda i: f"Page {i+1}",
        key=key,
        on_change=handle_page_change,
        kwargs={"page_size": page_size}
    )



def paginator(label, items, items_per_page=10, on_sidebar=True, page_number_key=None):
    """Lets the user paginate a set of items.
    Parameters
    ----------
    label : str
        The label to display over the pagination widget.
    items : Iterator[Any]
        The items to display in the paginator.
    items_per_page: int
        The number of items to display per page.
    on_sidebar: bool
        Whether to display the paginator widget on the sidebar.

    Returns
    -------
    Iterator[Tuple[int, Any]]
        An iterator over *only the items on that page*, including
        the item's index.
    Example
    -------
    This shows how to display a few pages of fruit.
    >>> fruit_list = [
    ...     'Kiwifruit', 'Honeydew', 'Cherry', 'Honeyberry', 'Pear',
    ...     'Apple', 'Nectarine', 'Soursop', 'Pineapple', 'Satsuma',
    ...     'Fig', 'Huckleberry', 'Coconut', 'Plantain', 'Jujube',
    ...     'Guava', 'Clementine', 'Grape', 'Tayberry', 'Salak',
    ...     'Raspberry', 'Loquat', 'Nance', 'Peach', 'Akee'
    ... ]
    ...
    ... for i, fruit in paginator("Select a fruit page", fruit_list):
    ...     st.write('%s. **%s**' % (i, fruit))
    """

    # Figure out where to display the paginator
    if on_sidebar:
        location = st.sidebar.empty()
    else:
        location = st.empty()

    # Display a pagination selectbox in the specified location.
    items = list(items)
    n_pages = len(items)
    n_pages = (len(items) - 1) // items_per_page + 1
    page_format_func = lambda i: "Page %s" % i
    _ = location.selectbox(
        label,
        range(n_pages),
        format_func=page_format_func,
        key=page_number_key,
        on_change=handle_page_change,
    )

    # Iterate over the items in the page to let the user display them.
    # st.session_state.min_idx = page_number * items_per_page
    # st.session_state.max_idx = st.session_state.min_idx + items_per_page
    # import itertools
    # st.session_state.selected_samples = items[min_index:max_index]
    # return itertools.islice(enumerate(items), st.session_state.min_idx, st.session_state.max_idx)
