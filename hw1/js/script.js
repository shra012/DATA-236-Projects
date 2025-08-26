const submissionCounter = (() => {
    let count = 0;
    return () => {
        count++;
        console.log(`Form has been successfully submitted ${count} time(s).`);
    };
})();

const validateForm = (formData) => {
    const {content, terms} = formData;

    if (content.length <= 25) {
        alert("Blog content should be more than 25 characters");
        return false;
    }

    if (!terms) {
        alert("You must agree to the terms and conditions");
        return false;
    }

    return true;
};

const displayBlog = (blog) => {
    const container = document.getElementById("publishedBlogs");
    const div = document.createElement("div");
    div.className = "blog-card";
    div.innerHTML = `
    <h3>${blog.title}</h3>
    <p id="blog-post-author"><strong>Author</strong> ${blog.author} (${blog.email})</p>
    <p id="blog-post-category"><strong>${blog.category}</strong></p>
    <p class="blog-post-content">${blog.content}</p>
    <small>Submitted at: ${blog.submissionDate}</small>
  `;
    container.prepend(div);
};

document.getElementById("blogForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = {
        title: document.getElementById("title").value.trim(),
        author: document.getElementById("author").value.trim(),
        email: document.getElementById("email").value.trim(),
        content: document.getElementById("content").value.trim(),
        category: document.getElementById("category").value,
        terms: document.getElementById("terms").checked,
    };

    if (!validateForm(formData)) return;
    const jsonString = JSON.stringify(formData);
    console.log("Form Data JSON:", jsonString);

    const parsedObj = JSON.parse(jsonString);
    const {title, email} = parsedObj;
    console.log("Extracted Title:", title);
    console.log("Extracted Email:", email);

    const updatedObj = {...parsedObj, submissionDate: new Date().toLocaleString()};
    console.log("Updated Object with submissionDate:", updatedObj);
    displayBlog(updatedObj);
    submissionCounter();

    await new Promise((resolve) => setTimeout(resolve, 500));
    console.log("Form submission simulated asynchronously.");
    event.target.reset();
});