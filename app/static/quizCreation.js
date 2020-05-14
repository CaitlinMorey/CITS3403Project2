function setRequired(inputs, required, hide) {
    for (x in inputs) {
        if (typeof inputs[x].id !== "undefined") {
            var idStr = inputs[x].id;
            if (required.some(v => idStr.includes(v))) {
                inputs[x].setAttribute("required", "");
                inputs[x].style.display = "initial";
                $("label[for=" + inputs[x].name + "]").show();
            } else {
                inputs[x].removeAttribute("required");
            }
            if (hide.some(v => idStr.includes(v))) {
                inputs[x].style.display = "none";
                $("label[for=" + inputs[x].name + "]").hide();
            }
        } else {
            continue;
        }
    }
}
/**
* Changes Question type
**/
function typeChange() {
    var $form = this.closest('.subform');
    var $quesForm = $(this).closest('.subform');
    var inputs = $form.getElementsByTagName('input')
    var type = this.value;
    if (type == "longAns") {
        var required = ["quizQuestion"]
        var hide = ["quizAnswer"]
        setRequired(inputs, required, hide)
        $quesForm.find(".option-container").addClass("is-hidden")
    } else if (type == "shortAns") {
        var required = ["quizQuestion", "quizAnswer"]
        var hide = ["None"]
        setRequired(inputs, required, hide)
        $quesForm.find(".option-container").addClass("is-hidden")
    } else if (type == "fillIn") {
        var required = ["quizQuestion", "quizAnswer"]
        var hide = ["None"]
        setRequired(inputs, required, hide)
        $quesForm.find(".option-container").addClass("is-hidden")
    } else {
        $quesForm.find(".option-container").removeClass("is-hidden")
        var required = ["quizQuestion", "quizAnswer", "option1"]
        var hide = ["None"]
        setRequired(inputs, required, hide)
    }


}

/** Code below taken and edited from: https://www.rmedgar.com/blog/dynamic-fields-flask-wtf */
/**
 * Adjust the indices of form fields when removing items.
 */
function adjustIndices(removedIndex) {
    var $forms = $('.subform');

    $forms.each(function (i) {
        var $form = $(this);
        var index = parseInt($form.data('index'));
        var newIndex = index - 1;

        if (index < removedIndex) {
            // Skip
            return true;
        }

        $form.find("p")[0].innerHTML = "Question: " + (newIndex + 1);
        // Change ID in form itself
        $form.attr('id', $form.attr('id').replace(index, newIndex));
        $form.attr('data-index', $form.attr('data-index').replace(index, newIndex));
        $form.data('index', newIndex);
        // Change IDs in form inputs
        $form.find('input').each(function (j) {
            var $item = $(this);
            $item.attr('id', $item.attr('id').replace(index, newIndex));
            $item.attr('name', $item.attr('name').replace(index, newIndex));
        });
        //Change labels id and name
        $form.find('label').each(function (k) {
            var $item = $(this);
            $item.attr('for', $item.attr('for').replace(index, newIndex));
        });
        //Change select field id and name
        $form.find('select').each(function (l) {
            var $item = $(this);
            $item.attr('id', $item.attr('id').replace(index, newIndex));
            $item.attr('name', $item.attr('name').replace(index, newIndex));
        });

    });

}


/**
 * Remove a form.
 */
function removeForm() {
    var $removedForm = $(this).closest('.subform');
    var removedIndex = parseInt($removedForm.data('index'));

    console.log(removedIndex)
    $removedForm.remove();

    // Update indices
    adjustIndices(removedIndex);
}

/**
 * Add a new form.
 */
function addForm() {
    var $templateForm = $('#quiz-_-form');

    if (!$templateForm) {
        console.log('[ERROR] Cannot find template');
        return;
    }

    // Get Last index
    var $lastForm = $('.subform').last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }

    // Maximum of 30 subforms
    if (newIndex > 30) {
        console.log('[WARNING] Reached maximum number of elements');
        return;
    }

    // Add elements
    var $newForm = $templateForm.clone();

    $newForm.attr('id', $newForm.attr('id').replace('_', newIndex));
    $newForm.attr('data-index', $newForm.attr('data-index').replace('_', newIndex))
    $newForm.data('index', newIndex);

    $newForm.find("p")[0].innerHTML += newIndex + 1;
    //Change input id and name
    $newForm.find('input').each(function (idx) {
        var $item = $(this);
        $item.attr('id', $item.attr('id').replace('_', newIndex));
        $item.attr('name', $item.attr('name').replace('_', newIndex));
    });
    //Change labels id and name
    $newForm.find('label').each(function (idx) {
        var $item = $(this);
        $item.attr('for', $item.attr('for').replace('_', newIndex));
    });
    //Change select field id and name
    $newForm.find('select').each(function (idx) {
        var $item = $(this);
        $item.attr('id', $item.attr('id').replace('_', newIndex));
        $item.attr('name', $item.attr('name').replace('_', newIndex));
    });

    // Append
    $('#subforms-container').append($newForm);
    $newForm.addClass('subform');
    $newForm.removeClass('is-hidden');
    $newForm.find('select')[0].onchange = typeChange;
    $newForm.find('.remove').click(removeForm);

}

function fScroll(val)
{
        var hidScroll = document.getElementById('hidScroll');
        hidScroll.value = val.scrollTop;
}

// function moves scroll position to saved value
function fScrollMove(what)
{
        var hidScroll = document.getElementById('hidScroll');
        document.getElementById(what).scrollTop = hidScroll.value;
}

$(document).ready(function () {
    $('#add').click(addForm);
    $('.remove').click(removeForm);
    document.getElementById('question-0-quesType').onchange = typeChange;
    document.getElementById('question-0-quizAnswer').setAttribute("required", "");
});
            /** Code above taken and edited from: https://www.rmedgar.com/blog/dynamic-fields-flask-wtf */