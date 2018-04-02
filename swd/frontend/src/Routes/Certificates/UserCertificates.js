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
        paddingBottom: 0
    },
    tableEntry: {
        paddingLeft: 15,
        fontFamily: 'Open Sans'
    },
    noCertificate: {
        marginLeft: 30,
        paddingBottom: 20
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
                        {bonafide.length?bonafide.map((bon) => {
                            return (
                                <div style={{display: 'flex', marginLeft: 20}} key={bonafide.indexOf(bon)}>
                                    <div style={{flexGrow: 1}}><h4 style={styles.tableEntry}>{bonafide.indexOf(bon)+1}</h4></div>
                                    <div style={{flexGrow: 3}}><h4 style={styles.tableEntry}>{bon.reason=="OTHER"?bon.otherReason:bon.reason.replace('_',' ')}</h4></div>
                                    <div style={{flexGrow: 3}}><h4 style={styles.tableEntry}>{bon.printed? "Printed": "Not Printed"}</h4></div>
                                </div>
                            )
                        }):<p style={styles.noCertificate}>No Certificates to show</p>}
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


export default graphql(bonafide, {options: (props) => ({variables: {username: props.username}})})(UserCertificates);