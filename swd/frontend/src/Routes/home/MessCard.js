import React from 'react';
import PropTypes from 'prop-types';
import {Card, CardActions, CardHeader, CardText} from 'material-ui/Card';
import FlatButton from 'material-ui/FlatButton';
import {RadioButton, RadioButtonGroup} from 'material-ui/RadioButton';
import ExpandableCard from "../../Components/ExpandableCard";

const MessChoiceForm = (props) => {
  
    const chooseMessAction = () => {
        // Send mutations here
    }
    return(
        <div>
    <RadioButtonGroup name="messChoice" >
      <RadioButton
        value="A"
        label="A"
      />
      <RadioButton
        value="C"
        label="C"
      />
    </RadioButtonGroup>
    <FlatButton label="Submit" onClick={chooseMessAction} primary={true} />
    </div>
    );
}

const MessCard = (props) => {

  const { messOptionOpen, messCurrentChoice } = props;

console.log(messOptionOpen)
console.log(messCurrentChoice)
let cardTitle = messOptionOpen.messoptionopen.openNow
  ? ("Mess option for the month of " + messOptionOpen.messoptionopen.month + " is open")
  : "Your current mess is " + messCurrentChoice.currentChoice.mess
console.log(messOptionOpen, "messOptionOpen")


  return(
<ExpandableCard title={cardTitle}> 
<MessChoiceForm/>
 </ExpandableCard>
  );
};

// Change these proptypes depedning on whether the error-handling mechanisms are
// implicit or explicit. Currently, they are assumed to be explicit.
MessCard.propTypes = {
  messOptionOpen: PropTypes.object.isRequired,
  messCurrentChoice: PropTypes.object.isRequired
};

export default MessCard;