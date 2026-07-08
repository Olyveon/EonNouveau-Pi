import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.VirtualKeyboard

ApplicationWindow {
    visible: true
    width: 1024
    height: 600
    title: "Main GUI"
    
    property int activeSection: 0

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ==========================================
        // HEADER
        // ==========================================
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "#0b0d13" }
                GradientStop { position: 1.0; color: "#2e1c1c" }
            }
            // Bottom border
            Rectangle {
                width: parent.width
                height: 2
                color: "#191c20"
                anchors.bottom: parent.bottom
            }

            Text {
                text: "Eon OS"
                color: "#FFFFFF"
                font.pixelSize: 20
                anchors.centerIn: parent
            }
        }

        // ==========================================
        // BODY
        // ==========================================
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            gradient: Gradient {
                orientation: Gradient.Vertical
                GradientStop { position: 0.0; color: "#0b0d13" }
                GradientStop { position: 1.0; color: "#2f1b31" }
            }

            RowLayout {
                anchors.fill: parent
                spacing: 0

                // Sidebar
                Rectangle {
                    Layout.fillHeight: true
                    Layout.preferredWidth: 200
                    color: "transparent"

                    ScrollView {
                        anchors.fill: parent
                        anchors.topMargin: 10
                        anchors.bottomMargin: 10
                        clip: true      
                        
                        // Restrict scrolling to vertical only
                        contentWidth: availableWidth
                        contentHeight: column.implicitHeight
                        
                        // Hide scrollbars for cleaner touch interface
                        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                        ScrollBar.vertical.policy: ScrollBar.AlwaysOff

                        Column {
                            id: column
                            anchors.horizontalCenter: parent.horizontalCenter
                            spacing: 20

                            Button {
                                text: "Apps"; width: 180; height: 60; onClicked: activeSection = 0 
                                background: Rectangle {
                                    color: activeSection === 0 ? "#331f1f" : "#191723"
                                    radius: 10
                                    border.color: activeSection === 0 ? "#fc724f" : "#25282c"
                                    border.width: 2
                                }
                                contentItem: Text { text: parent.text; color: activeSection === 0 ? "#fc724f" : "#8a8d94"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                            }
                            Button { 
                                text: "Red"; width: 180; height: 60; onClicked: activeSection = 1 
                                background: Rectangle { 
                                    color: activeSection === 1 ? "#331f1f" : "#191723"
                                    radius: 10
                                    border.color: activeSection === 1 ? "#fc724f" : "#25282c"
                                    border.width: 2
                                }
                                contentItem: Text { text: parent.text; color: activeSection === 1 ? "#fc724f" : "#8a8d94"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                            }
                            Button { 
                                text: "Bluetooth"; width: 180; height: 60; onClicked: activeSection = 2 
                                background: Rectangle { 
                                    color: activeSection === 2 ? "#331f1f" : "#191723"
                                    radius: 10
                                    border.color: activeSection === 2 ? "#fc724f" : "#25282c"
                                    border.width: 2
                                }
                                contentItem: Text { text: parent.text; color: activeSection === 2 ? "#fc724f" : "#8a8d94"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                            }
                            Button { 
                                text: "Game Boy Advance"; width: 180; height: 60; onClicked: activeSection = 3 
                                background: Rectangle { 
                                    color: activeSection === 3 ? "#331f1f" : "#191723"
                                    radius: 10
                                    border.color: activeSection === 3 ? "#fc724f" : "#25282c"
                                    border.width: 2
                                }   
                                contentItem: Text { text: parent.text; color: activeSection === 3 ? "#fc724f" : "#8a8d94"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                            }
                        }
                    }
                }

                // Main Content Container
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "transparent"

                    StackLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        currentIndex: activeSection

                        Apps {}
                        Network {}
                        Bluetooth {}
                        Text {
                            text: "Game Boy Advance Section"
                            color: "#FFF"
                            font.pixelSize: 20
                            Layout.alignment: Qt.AlignCenter
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // VIRTUAL KEYBOARD INTEGRATION
    // ==========================================
    InputPanel {
        id: inputPanel
        parent: Overlay.overlay // Esto lo mueve a la capa de superposición global de Qt Quick
        z: 99999 // Un valor de Z ridículamente alto para ganar a cualquier Popup
        x: 0
        y: parent.height // Oculto por defecto (fuera de la pantalla por debajo)
        width: parent.width

        states: State {
            name: "visible"
            // Cuando activo, el InputPanel sube y se muestra
            when: inputPanel.active
            PropertyChanges {
                target: inputPanel
                y: parent.height - inputPanel.height
            }
        }

        transitions: Transition {
            from: ""
            to: "visible"
            reversible: true
            ParallelAnimation {
                NumberAnimation {
                    properties: "y"
                    duration: 250
                    easing.type: Easing.InOutQuad
                }
            }
        }
    }
}