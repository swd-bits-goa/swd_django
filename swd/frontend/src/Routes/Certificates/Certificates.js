import React from 'react';
import Paper from 'material-ui/Paper';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import TextField from 'material-ui/TextField';
import RaisedButton from 'material-ui/RaisedButton';
import UserCertificates from './UserCertificates.js';
import {graphql} from 'react-apollo';
import gql from 'graphql-tag';
import { bonafide } from './UserCertificates.js';
import { compose } from 'react-apollo';
import { Mutation } from "react-apollo";


const styles = {
    container: {
        minHeight: 600
    },
    formContainer: {
        margin: 5,
        borderRadius: 7,
    },
    header: {
        fontFamily: 'Open Sans',
        padding: 20,
        paddingLeft: 30,
        marginBottom: 0,
        paddingBottom: 0
    },
    dropdown: {
        marginLeft: 30,
        width: '85%'
    },
    textField: {
        marginLeft: 30,
        width: '85%'
    },
    submitButton: {
        width: '50%',
        margin: 15,
        marginBottom: 8,
        marginLeft: '25%'
    },
    errorMessage: {
        padding: 25,
        color: 'red'
    }
}

class Certificates extends React.Component{
    constructor(){
        super();
        this.state = {
            reason: "Bank Loan",
            username: "",
            other: "",
            clicked: false,
            specifyReason: false
          };
          this.handleChange = this.handleChange.bind(this)
    }
    handleChange = (event, index, value) => this.setState({reason: value});
    
    render(){
        /*const submitBonafideApplication = (e) => {
            console.log('in here');
            console.log(this.state.other);
            console.log(this.state.reason);
            var otherReason;
            if(this.state.reason==="Other"){
                otherReason = this.state.other;
            }  
            console.log(this.props) 
            const mutate=this.props.mutate;
            mutate({
                variables: {
                    reason: this.state.reason,
                    otherReason: otherReason
                },
                /*update: (store, {data: {submitBonafideApplication}}) => {
                    const data = store.readQuery({query: bonafide});
                    data.bonafide.push(submitBonafideApplication);
                    store.writeQuery({query: bonafide, data});
                }
                refetchQueries: [{query: bonafide}]
            }).then(res => {
                console.log('done');
            })
    
        }*/
        const { loading, error, currentUser } = this.props.data;
        var otherReason;
        if(this.state.reason==="Other"){
            otherReason = this.state.other;
        } 
        if(loading)
            return <p>loading</p>
        else if(error)
            return <p>Error</p>
        if(!currentUser)
            return <h3>You need to login first</h3>
        return(
            <div style={styles.container}>
            <Mutation mutation={submitApplication} refetchQueries={[{query: bonafide, variables: {username: currentUser.username}}]}>
                {(submitBonafideApplication, { data }) => (
                    <Paper zDepth={1} style={styles.formContainer}>
                        <h2 style={styles.header}>Apply for bonafide certificate</h2>
                        <SelectField
                            floatingLabelText="Reason"
                            hintText="Reason"
                            value={this.state.reason}
                            onChange={this.handleChange}
                            style={styles.dropdown}
                            labelStyle={{fontSize: 21}}
                            >
                            <MenuItem value={"Bank Loan"} primaryText="Bank loan" />
                            <MenuItem value={"Passport"} primaryText="Passport" />
                            <MenuItem value={"Other"} primaryText="Other" />
                        </SelectField>
                        <TextField
                            hintText="Please mention if other reason"
                            style={styles.textField}
                            multiLine={true}
                            value={this.state.other}
                            onChange = {(e, val) => this.setState({other: val})}
                            ref={input => this.input=input}
                            disabled={!(this.state.reason==="Other")}/>
                        {console.log(this.state.reason)}
                        <RaisedButton label="Submit" 
                            primary={true} style={styles.submitButton} 
                            onClick={(e) => 
                                {
                                    this.setState({clicked: true}); 
                                    if(this.state.reason==="Other") 
                                        var otherReason=this.state.other;
                                    if(this.state.reason=="Other"&&!otherReason)
                                    {
                                        this.setState({specifyReason: true});
                                    }
                                    else{
                                        submitBonafideApplication({variables: {reason: this.state.reason, otherReason: otherReason}})};
                                        this.setState({specifyReason: false});
                                        this.setState({reason:"Bank Loan",other: ""})
                                    }    
                                    
                                    
                                }/>
                        {this.state.clicked&&data&&!data.submitBonafideApplication?<p style={styles.errorMessage}>You have already applied for bonafide thrice in this semester</p>:null}
                        {this.state.clicked&&this.state.reason==="Other"&&!this.input.state.hasValue?<p style={styles.errorMessage}>You must specify reason</p>:null}
                    </Paper>
                )

                }
            </Mutation>
            <UserCertificates username={currentUser.username}/>
            </div>
        )
    }
}



const currentUser = gql`
    query currentUser{
        currentUser{
            username
        }
    }
`;

const submitApplication = gql`
    mutation submitBonafideApplication($reason: String!, $otherReason: String){
        submitBonafideApplication(reason: $reason, otherReason: $otherReason){
            bonafide{
                reason
                printed
                otherReason
            }
        }
    }
`;

export default compose(graphql(currentUser), graphql(submitApplication))(Certificates);

