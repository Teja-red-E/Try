// script.js

// Example function to fetch and display shirt images dynamically
async function fetchShirts() {
    const response = await fetch('/api/shirts'); // Assuming Streamlit app serves shirts via this endpoint
    const shirts = await response.json();

    const shirtContainer = document.querySelector('.shirt-container');
    shirtContainer.innerHTML = '';

    shirts.forEach(shirt => {
        const shirtItem = document.createElement('div');
        shirtItem.classList.add('shirt-item');

        const shirtImg = document.createElement('img');
        shirtImg.src = shirt.imageUrl;
        shirtImg.alt = shirt.name;

        const tryOnButton
