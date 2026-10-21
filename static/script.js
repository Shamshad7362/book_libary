document.addEventListener('DOMContentLoaded', () => {
    const savedScrollPosition = sessionStorage.getItem('libraryScrollPosition');
    if (savedScrollPosition !== null) {
        sessionStorage.removeItem('libraryScrollPosition');
        requestAnimationFrame(() => window.scrollTo(0, Number(savedScrollPosition)));
    }

    const form = document.querySelector('.book-form');
    const searchInput = document.getElementById('author-search');
    const authorIdInput = document.getElementById('author-id');
    const results = document.getElementById('author-results');
    const noResults = results.querySelector('.author-no-results');
    const newAuthorButton = document.getElementById('show-new-author');
    const newAuthorFields = document.getElementById('new-author-fields');
    const authorNameInput = document.getElementById('author-name');
    const countryInput = document.getElementById('country');
    const duplicateAuthorWarning = document.getElementById('duplicate-author-warning');
    const authorOptions = Array.from(results.querySelectorAll('.author-result'));
    const bookSearch = document.getElementById('book-search');
    const flashBox = document.querySelector('.flash-messages');
    const nameInput = document.getElementById('name');


    let previousAuthor = null;

    function checkForDuplicateAuthor() {
        const typedName = authorNameInput.value.trim().toLocaleLowerCase();
        const duplicate = typedName
            ? authorOptions.find((option) => option.dataset.authorName.trim().toLocaleLowerCase() === typedName)
            : null;

        duplicateAuthorWarning.hidden = !duplicate;
        if (duplicate) {
            duplicateAuthorWarning.textContent = `“${duplicate.dataset.authorName}” already exists. Cancel and select the existing author from the list.`;
            authorNameInput.setCustomValidity('This author already exists. Select the existing author instead.');
        } else {
            duplicateAuthorWarning.textContent = '';
            authorNameInput.setCustomValidity('');
        }
        return duplicate;
    }

    if (flashBox && nameInput) {
    nameInput.addEventListener('input', () => {
        flashBox.hidden = true;
    });
}

    authorNameInput.addEventListener('input', checkForDuplicateAuthor);

    if (bookSearch) {
        const bookRows = Array.from(document.querySelectorAll('.book-row'));
        const noBookMatches = document.getElementById('book-search-empty');

        bookSearch.addEventListener('input', () => {
            const query = bookSearch.value.trim().toLocaleLowerCase();
            let visibleBooks = 0;

            bookRows.forEach((row) => {
                const matches = row.textContent.toLocaleLowerCase().includes(query);
                row.hidden = !matches;
                if (matches) visibleBooks += 1;
            });

            noBookMatches.hidden = visibleBooks > 0;
        });
    }

    const deleteDialog = document.getElementById('delete-confirm');
    if (deleteDialog) {
        const cancelDelete = document.getElementById('cancel-delete');
        const confirmDelete = document.getElementById('confirm-delete');
        const deleteBookTitle = document.getElementById('delete-book-title');
        let pendingDeleteForm = null;

        document.querySelectorAll('.delete-form').forEach((deleteForm) => {
            deleteForm.addEventListener('submit', (event) => {
                if (deleteForm.dataset.confirmed === 'true') {
                    deleteForm.dataset.confirmed = 'false';
                    return;
                }

                event.preventDefault();
                pendingDeleteForm = deleteForm;
                deleteBookTitle.textContent = deleteForm.dataset.bookTitle;
                deleteDialog.showModal();
            });
        });

        cancelDelete.addEventListener('click', () => {
            pendingDeleteForm = null;
            deleteDialog.close();
        });

        confirmDelete.addEventListener('click', () => {
            if (!pendingDeleteForm) return;
            const formToDelete = pendingDeleteForm;
            pendingDeleteForm = null;
            sessionStorage.setItem('libraryScrollPosition', String(window.scrollY));
            formToDelete.dataset.confirmed = 'true';
            deleteDialog.close();
            formToDelete.requestSubmit();
        });

        deleteDialog.addEventListener('click', (event) => {
            if (event.target === deleteDialog) deleteDialog.close();
        });

        deleteDialog.addEventListener('close', () => {
            pendingDeleteForm = null;
        });
    }

    function setNewAuthorMode(isAdding) {
        newAuthorFields.hidden = !isAdding;
        authorNameInput.required = isAdding;
        countryInput.required = isAdding;
        searchInput.disabled = isAdding;
        searchInput.required = !isAdding;
        newAuthorButton.textContent = isAdding ? 'Cancel adding author' : '＋ Add a new author';
        newAuthorButton.classList.toggle('is-cancel', isAdding);
        if (isAdding) {
            duplicateAuthorWarning.hidden = true;
            duplicateAuthorWarning.textContent = '';
            authorNameInput.setCustomValidity('');
            hideResults();
            authorNameInput.focus();
        } else {
            authorNameInput.value = '';
            authorNameInput.setCustomValidity('');
            countryInput.value = '';
            duplicateAuthorWarning.hidden = true;
            duplicateAuthorWarning.textContent = '';
        }
    }

    function showResults() {
        results.hidden = false;
        searchInput.setAttribute('aria-expanded', 'true');
    }

    function hideResults() {
        results.hidden = true;
        searchInput.setAttribute('aria-expanded', 'false');
    }

    function filterAuthors() {
        const query = searchInput.value.trim().toLocaleLowerCase();
        let visibleCount = 0;

        authorOptions.forEach((option) => {
            const matches = option.dataset.authorName.toLocaleLowerCase().includes(query);
            option.hidden = !matches;
            if (matches) visibleCount += 1;
        });

        noResults.hidden = visibleCount > 0;
        showResults();
    }

    function chooseExistingAuthor(option) {
        searchInput.value = option.dataset.authorName;
        authorIdInput.value = option.dataset.authorId;
        searchInput.required = true;
        searchInput.disabled = false;
        searchInput.setCustomValidity('');
        setNewAuthorMode(false);
        hideResults();
    }

    searchInput.addEventListener('focus', filterAuthors);
    searchInput.addEventListener('input', () => {
        authorIdInput.value = '';
        searchInput.setCustomValidity('');
        filterAuthors();
    });

    results.addEventListener('click', (event) => {
        const option = event.target.closest('.author-result');
        if (option) chooseExistingAuthor(option);
    });

    newAuthorButton.addEventListener('click', () => {
        if (authorIdInput.value === 'new') {
            authorIdInput.value = previousAuthor.id;
            searchInput.value = previousAuthor.name;
            previousAuthor = null;
            setNewAuthorMode(false);
            return;
        }

        previousAuthor = {
            id: authorIdInput.value,
            name: searchInput.value,
        };
        authorIdInput.value = 'new';
        searchInput.value = '';
        searchInput.setCustomValidity('');
        setNewAuthorMode(true);
    });

    searchInput.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') hideResults();
        if (event.key === 'ArrowDown' && !results.hidden) {
            const firstOption = authorOptions.find((option) => !option.hidden);
            if (firstOption) {
                event.preventDefault();
                firstOption.focus();
            }
        }
    });

    results.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            hideResults();
            searchInput.focus();
        }
    });

    document.addEventListener('click', (event) => {
        if (!results.contains(event.target) && event.target !== searchInput) hideResults();
    });

    // form.addEventListener('submit', (event) => {
    //     if (authorIdInput.value === 'new' && checkForDuplicateAuthor()) {
    //         event.preventDefault();
    //         authorNameInput.reportValidity();
    //         return;
    //     }
    //     if (!authorIdInput.value) {
    //         event.preventDefault();
    //         searchInput.setCustomValidity('Choose an author from the suggestions or add a new author.');
    //         searchInput.reportValidity();
    //     }
    // });
});
