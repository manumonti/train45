pragma solidity ^0.8.0;

interface IReceiver {
    function receiveMessage(bytes memory inputData) external;
}
