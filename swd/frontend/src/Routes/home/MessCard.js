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

  const {messOption} = props;
 
  const { messoptionopen, messoption } = messOption;

console.log(messoptionopen)
console.log(messoption)
let cardTitle = messoptionopen.openNow
  ? ("Mess option for the month of " + messoptionopen.month + " is open")
  : "Your current mess is " + messoption.mess
console.log(messoptionopen, "messoptionopen")


  return(
<ExpandableCard title={cardTitle}> 
<MessChoiceForm/>
 </ExpandableCard>
  );
};

// Change these proptypes depedning on whether the error-handling mechanisms are
// implicit or explicit. Currently, they are assumed to be explicit.
MessCard.propTypes = {
  messOption: PropTypes.object.isRequired,
};

export default MessCard;