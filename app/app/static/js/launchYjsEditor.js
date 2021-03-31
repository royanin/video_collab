    function launchEditor(name_, room_){

            window.Y = yjquill.Y;
            window.WebsocketProvider = yjquill.WebsocketProvider;
            window.QuillBinding = yjquill.QuillBinding;
            window.Quill = yjquill.Quill;
            window.QuillCursors = yjquill.QuillCursors;

            Quill.register('modules/cursors', QuillCursors);

            window.addEventListener('load', () => {
              const ydoc = new Y.Doc()
              const provider = new WebsocketProvider('wss://demos.yjs.dev', room_, ydoc)
              //const provider = new WebsocketProvider('wss://localhost:1234', "{{ session.room }}", ydoc)
              const ytext = ydoc.getText('quill')
              //const editorContainer = document.createElement('div')
              //editorContainer.setAttribute('id', 'editor')
              //document.body.insertBefore(editorContainer, null)

              const editor = new Quill('#editor2', {
                modules: {
                  cursors: true,
                  toolbar: [
                    [{ header: [1, 2, false] }],
                    ['bold', 'italic', 'underline'],
                    ['code-block']
                  ],
                  history: {
                    userOnly: true
                  }
                },
                placeholder: 'Make a copy of your notes before leaving the room.',
                theme: 'snow' // or 'bubble'
              })

              binding = new QuillBinding(ytext, editor, provider.awareness)



              // Define user name and user name
              // Check the quill-cursors package on how to change the way cursors are rendered
              provider.awareness.setLocalStateField('user', {
                //name: '{{ session.name }}',
                name: name_,
                color: 'blue'
              })
            })
    }
