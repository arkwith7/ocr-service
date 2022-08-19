$(function(){
    // ===================================================
        
        function objectToTable(obj) {
            var table = $('<table>').append('<tbody>');
            for ( var key in obj ) {
            var tr = $('<tr>');
            var th = $('<th>').append(key);
            var td = $('<td>');
            var value;
            if ( typeof(obj[key]) == 'object' ) {
                if ( obj[key] ) {
                    value = objectToTable(obj[key]);
                }
                else {
                    value = '<span class="null">null</span>';
                }
            }
            else if ( typeof(obj[key]) == 'boolean' ) {
                var str = (obj[key]) ? 'true' : 'false';
                value = '<span class="boolean">'+str+'</span>'; 
            }
            else if ( typeof(obj[key]) == 'string' ) {
                value = '<span class="string">"'+obj[key]+'"</span>';
            }
            else {
                value = obj[key].valueOf();
            }
            td.append(value);
            tr.append(th).append(td);
            table.append(tr);
            }
            return table;
        }
        
        $('#show_button').click(function(){
            var value = '';
            var source = $('#source').val();
            if ( source ) {
            try {
                value = objectToTable(eval("("+source+")"));
            } catch (e) {
                value = '<pre>'+e+'</pre>';
            }
            }
            $('#container').empty().append(value);
        });
        
        $(document).ready(function(){
            $('#show_button').trigger('click');
        });
    
        $('#source')
            .live('drop', function(e){
                e.stopPropagation();
                e.preventDefault();
                $(this).removeClass('over');
                var files = e.originalEvent.dataTransfer.files;
                    if ( files && files.length > 0 ) {
                        var file = files[0];
                        var reader = new FileReader();
                        reader.onload = function(event)	{
                            //console.log(this.result);
                            $('#source').val(this.result);
                            $('#show_button').trigger('click');
                        }
                        reader.readAsText(file);
                    }
                })
            .live('dragenter', function(e){
                e.stopPropagation();
                e.preventDefault();
                $(this).addClass('over');
            })
            .live('dragleave', function(e){
                e.stopPropagation();
                e.preventDefault();
                $(this).removeClass('over');
            });
        
    // ===================================================
    });