
function renderNoteTemplate(note){
	return `
	<div class="note" id="application_note-${note.id}">
    <div class="note-time">${note.created}</div>
    <div class="note-body">${note.body}</div>
    <div class="note-author">-${note.user}</div>
    <div class="note-remove" title="Delete this note">
      <button class="btn btn-danger btn-sm">
      <span class="glyphicon glyphicon-remove-sign"></span> Delete</a>
    </div>
  </div>
	`;
}

module.exports = {
  note: renderNoteTemplate,
}