import React from 'react';
import {graphql} from 'react-apollo';
import gql from 'graphql-tag';
import Paper from 'material-ui/Paper';

const styles = {
    formContainer: {
        margin: 5,
        borderRadius: 7,
    },
    header: {
        fontFamily: 'Open Sans',
        padding: 20,
        paddingLeft: 30,
        marginBottom: 0,
        paddingBottom: 10
    },
    tableEntry: {
        paddingLeft: 15,
        fontFamily: 'Open Sans'
    }
}

class UserCertificates extends React.Component{
    render(){
            const {loading, error, bonafide } = this.props.data;
            if(loading)
                return <p>loading</p>
            if(error)
                return <p>{error.message}</p>
            return (<Paper zDepth={1} style={styles.formContainer}>
                        <h2 style={styles.header}>Bonafide Applications</h2>
                        {bonafide?bonafide.map((bon) => {
                            return (
                                <div key={bonafide.indexOf(bon)+1} style={{display: 'flex', marginLeft: 20}}>
                                    <div style={{flexGrow: 1}}><h4 style={styles.tableEntry}>{bonafide.indexOf(bon)+1}</h4></div>
                                    <div style={{flexGrow: 3}}><h4 style={styles.tableEntry}>{bon.reason=="OTHER"?bon.otherReason:bon.reason.replace('_',' ')}</h4></div>
                                    <div style={{flexGrow: 3}}><h4 style={styles.tableEntry}>{bon.printed? "Printed": "Not Printed"}</h4></div>
                                </div>
                            )
                        }):<p>Nothing to show here!</p>}
                    </Paper>
                )
    }
}


const bonafide = gql`
    query bonafide($username: String!){
        bonafide(username: $username){
            reason
            printed
            otherReason
        }
    }
`;

export { bonafide };
export default graphql(bonafide, {options: (props) => ({variables: {username: props.username}})})(UserCertificates);
