function triggerOnBlur(inputId, promptId) {
    const inputField = document.getElementById(inputId);
    let prompt = document.getElementById(promptId);

    if (inputField.value === "") {
        prompt.textContent = "*Required"
        prompt.style.display = "inline";
    } else {
        prompt.textContent = ""
        prompt.style.display = "none";
    }
}

function triggerOnFocus(promptId) {
    let prompt = document.getElementById(promptId);
    prompt.textContent = "";
    prompt.style.display = "none";
}

// var signupFormEle = document.getElementById("signUpForm");

// signupFormEle.addEventListener("submit", function(event) {
//     event.preventDefault();
//     validateMobileNumber();
//     validatePassword();
//     confirmPassword();

// })

function validateForm(){
    if(validateMobileNumber() && validatePassword() && confirmPassword()){
        // console.log("validation successful");
        return true;
    }
    else{
        return false;
    }
}

function validatePassword() {
    var passwordEle = document.getElementById("passwordInSignUp");
    var password = passwordEle.value;
    var passwordPromt = document.getElementById("passwordPrompt");

    if (passwordEle.value.length < 8) {
        passwordPromt.textContent = "*Password should contain atleast 8 characters";
        passwordPromt.style.display = "inline";
        return false;
        } else {
        var capLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        var smallLetters = "abcdefghijklmnopqrstuvwxyz";
        var digits = '1234567890';
        var specialChars = "<>@!#$%^&*()_+[]{}?:;|'\"\\,./~`-=";
        var capTest = false;
        var smallTest = false;
        var digitTest = false;
        var specialCharcTest = false;
        for (var i = 0; i < password.length; i++) {
            if (capLetters.includes(password[i])) {
                capTest = true;
            } else if (smallLetters.includes(password[i])) {
                smallTest = true;
            } else if (digits.includes(password[i])) {
                digitTest = true;
            } else if (specialChars.includes(password[i])) {
                specialCharcTest = true;
            }
        }
        if (!capTest) {
            passwordPromt.textContent = "*Password should contain atleast one capital letter";
            passwordPromt.style.display = "inline";
            return false;

        } else if (!smallTest) {
            passwordPromt.textContent = "*Password should contain atleast one small letter";
            passwordPromt.style.display = "inline";
            return false;

        } else if (!digitTest) {
            passwordPromt.textContent = "*Password should contain atleast one digit";
            passwordPromt.style.display = "inline";
            return false;

        } else if (!specialCharcTest) {
            passwordPromt.textContent = "*Password should contain atleast one special character";
            passwordPromt.style.display = "inline";
            return false;

        }
    }
    return true;
}

function validateMobileNumber() {
    var mobileNumberEle = document.getElementById("mobile_number");
    var mobileNumber = mobileNumberEle.value;
    var mobileNumberPrompt = document.getElementById("mobileNumberPrompt");

    if (mobileNumber.length !== 10) {
        mobileNumberPrompt.textContent = "*Mobile number should contain only 10 digits";
        mobileNumberPrompt.style.display = "inline";
        return false;
    }
    return true;
}



function confirmPassword() {
    var confirmPasswordEle = document.getElementById("conifrm_password_in_signup");

    var confirmPasswordPrompt = document.getElementById("confirmPasswordPrompt");
    var passwordEle = document.getElementById("passwordInSignUp");
    if (confirmPasswordEle.value !== passwordEle.value) {
        confirmPasswordPrompt.textContent = "*Should contain same value as password";
        confirmPasswordPrompt.style.display = "inline";
        return false;
    }
    return true;
}