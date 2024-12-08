export const createSunEditor = (target) => {
  return SUNEDITOR.create(target, {
    buttonList: [
      ["undo", "redo"],
      ["bold", "italic", "underline", "strike", "subscript", "superscript", "list"],
    ],
  });
};
