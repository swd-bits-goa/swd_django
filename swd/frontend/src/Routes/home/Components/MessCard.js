import React from 'react';
import PropTypes from 'prop-types';
import {Card, CardActions, CardHeader, CardText} from 'material-ui/Card';
import FlatButton from 'material-ui/FlatButton';
import {RadioButton, RadioButtonGroup} from 'material-ui/RadioButton';
import gql from "graphql-tag";
import {graphql, compose} from "react-apollo";
import Snackbar from 'material-ui/Snackbar';
import ExpandableCard from "../../../Components/ExpandableCard/ExpandableCard";

// TODO: Remove the need to provide date for mutation
const messChoiceMutation = gql`
mutation updateMess($mess: String!){
  updateMessOption(mess: $mess, month: "2016-04-01") {
 		messoption {
 		  id
 		}
  }
}`;

class MessChoiceForm extends React.Component {

  constructor(props) {
    super(props);
    this.state = { messChangeStatus: false,
    selectedRadio: "A" };

  }
  
  chooseMessAction = async () => {
        // Send mutations here
        await this.props.mutate({
          variables: {
            mess: this.state.selectedRadio
          },
          update: (data) => {
            // Seems like request is successful
            this.setState({messChangeStatus: true});
          }
        });
    }

  reflectRadio = (event, value) => {
    this.setState({selectedRadio: value,
    messChangeStatus: false});
  }

    render() {

    return(
        <div>
    <RadioButtonGroup name="messChoice" defaultSelected="A" onChange={this.reflectRadio}>
      <RadioButton
        value="A"
        label="A"
      />
      <RadioButton
        value="C"
        label="C"
      />
    </RadioButtonGroup>
    <FlatButton label="Submit" onClick={this.chooseMessAction} primary={true} />
    <Snackbar
          open={this.state.messChangeStatus}
          message={"Mess succesfully changed to " + this.state.selectedRadio + "!"}
          autoHideDuration={4000}
          
        />
    </div>
    );
}
}

const MessCard = (props) => {

  const {messOption} = props;
 
  const { messoptionopen, messoption } = messOption;

let showMessForm = false;
let cardTitle = "";

// Here we're assuming that messoptionopen return null if it is not open
if (messoptionopen && !messoption)
{
  cardTitle = "Mess option for the month of " + messoptionopen.month + " is open";
  showMessForm = true;
}
else
{
  cardTitle = "Your current mess is " + messoption.mess;
  showMessForm = false;
}

console.log(messoptionopen, "messoptionopen")
const MessChoiceFormWithMut = graphql(messChoiceMutation)(MessChoiceForm);

  return(
<ExpandableCard title={cardTitle}> 
{ 
  showMessForm
? <MessChoiceFormWithMut/>
: null
}
 </ExpandableCard>
  );
};

// Change these proptypes depedning on whether the error-handling mechanisms are
// implicit or explicit. Currently, they are assumed to be explicit.
MessCard.propTypes = {
  // Prop should be renamed to convey better meaning
  messOption: PropTypes.object.isRequired,
};

export default MessCard;