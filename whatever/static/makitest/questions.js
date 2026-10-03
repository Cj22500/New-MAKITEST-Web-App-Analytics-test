"use strict";
const questionForm = document.getElementById("question-form"),
  type = document.getElementById("id_question_type"),
  list = document.getElementById("choices-list");
function renumber() {
  [...list.children].forEach((row, index) => {
    const number = index + 1;
    for (const field of row.querySelectorAll("input")) {
      if (field.name === "correct_choice") field.value = number;
      else field.name = field.name.replace(/_\d+$/, "_" + number);
    }
  });
}
function toggle() {
  const mcq = type.value === "MCQ";
  document.getElementById("choices-editor").hidden = !mcq;
  list.querySelectorAll("input").forEach((field) => (field.disabled = !mcq));
  for (const id of ["id_correct_answer_text", "id_correct_answer_image"]) {
    const field = document.getElementById(id);
    if (field) {
      field.closest(".field").hidden = mcq || id === "id_correct_answer_image";
      field.disabled = mcq || id === "id_correct_answer_image";
    }
  }
}
type.addEventListener("change", toggle);
toggle();
document.getElementById("add-choice").onclick = () => {
  const row = document.createElement("div");
  row.className = "choice-row";
  row.innerHTML =
    '<label>Choice text<input name="choice_text_0"></label><label><input type="radio" name="correct_choice" value="0"> Correct answer</label><label>Choice image (optional)<input type="file" name="choice_image_0" accept="image/*"></label><label>Image description<input name="choice_description_0"></label><button class="btn ghost" type="button" data-remove-choice>Remove choice</button>';
  list.append(row);
  renumber();
  row.querySelector("input").focus();
};
list.addEventListener("click", (event) => {
  if (event.target.closest("[data-remove-choice]")) {
    event.target.closest(".choice-row").remove();
    renumber();
  }
});
questionForm.addEventListener("submit", renumber);
