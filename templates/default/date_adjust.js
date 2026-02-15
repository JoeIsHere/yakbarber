function localizeDates() {
  const dateElements = document.querySelectorAll('.date date');

  dateElements.forEach(dateElement => {
    const datetimeString = dateElement.getAttribute('datetime');
    if (datetimeString) {
      const date = new Date(datetimeString);
      if (!isNaN(date)) {
        const localizedString = date.toLocaleString(undefined, {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: 'numeric',
          minute: 'numeric',
        });
        dateElement.textContent = localizedString;
      } else {
        console.error("Invalid date format:", datetimeString);
      }
    }
  });
}

// Call the function when the DOM is loaded
document.addEventListener('DOMContentLoaded', localizeDates);